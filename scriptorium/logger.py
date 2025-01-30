import logging
import json
import queue
import threading
import contextlib
import time
from typing import Optional, Dict, Any, Generator
from logging.handlers import QueueHandler, QueueListener
from rich.logging import RichHandler
from .handlers import CompressedRotatingFileHandler, CompressedTimedRotatingFileHandler

_log_context: Dict[str, Any] = {}

class BatchHandler(logging.Handler):
    
    def __init__(self, target_handler: logging.Handler, capacity: int = 1000, 
                 flush_interval: float = 1.0):
        super().__init__()
        self.target_handler = target_handler
        self.buffer: list = []
        self.capacity = capacity
        self.flush_interval = flush_interval
        self.last_flush = time.time()
        self._lock = threading.Lock()
        self._shutdown = threading.Event()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        
    def _flush_loop(self):
        while not self._shutdown.is_set():
            time.sleep(0.1)
            if self.shouldFlush():
                self.flush()
        
    def shouldFlush(self) -> bool:
        with self._lock:
            return (len(self.buffer) >= self.capacity or 
                   (self.buffer and time.time() - self.last_flush >= self.flush_interval))
    
    def emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            record_copy = logging.LogRecord(
                name=record.name,
                level=record.levelno,
                pathname=record.pathname,
                lineno=record.lineno,
                msg=record.msg,
                args=record.args,
                exc_info=record.exc_info,
            )
            for attr in record.__dict__:
                if not hasattr(record_copy, attr):
                    setattr(record_copy, attr, getattr(record, attr))
            
            record_copy.getMessage()
            self.buffer.append(record_copy)
    
    def flush(self) -> None:
        records_to_process = []
        with self._lock:
            if self.buffer:
                records_to_process = self.buffer[:]
                self.buffer.clear()
                self.last_flush = time.time()
        
        for record in records_to_process:
            try:
                self.target_handler.emit(record)
            except Exception as e:
                print(f"Error in batch handler: {e}")
    
    def close(self) -> None:
        self._shutdown.set()
        self._flush_thread.join(timeout=1.0)
        self.flush()
        super().close()

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.context = getattr(record, "context", {})
        for key, value in _log_context.items():
            setattr(record, key, value)
        return True

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "context": getattr(record, "context", {}),
        }
        
        for key, value in record.__dict__.items():
            if (not key.startswith('_') and 
                key not in log_record and 
                key not in ('args', 'msg', 'exc_info', 'exc_text')):
                log_record[key] = value
        
        if hasattr(record, "exc_info") and record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record, ensure_ascii=False)

log_queue = queue.Queue(-1)
queue_handler = QueueHandler(log_queue)
queue_listener = None

@contextlib.contextmanager
def log_context(**kwargs: Any) -> Generator[None, None, None]:
    global _log_context
    token = object()
    previous = _log_context.copy()
    _log_context.update(kwargs)
    try:
        yield
    finally:
        _log_context.clear()
        _log_context.update(previous)

def get_logger(
    name: str,
    structured: bool = True,
    color: bool = True,
    async_logging: bool = False,
    batch_logging: bool = False,
    batch_size: int = 1000,
    batch_interval: float = 1.0,
    log_file: Optional[str] = None
) -> logging.Logger:
    global queue_listener

    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            try:
                handler.close()
            except Exception as e:
                print(f"Error closing handler: {e}")
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)

    handlers = []
    
    formatter = JSONFormatter() if structured else logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    context_filter = ContextFilter()
    
    if color and not structured:
        console_handler = RichHandler()
    else:
        console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    handlers = []
    
    if async_logging:
        if not queue_listener:
            queue_listener = QueueListener(log_queue, console_handler)
            queue_listener.start()
        final_handler = queue_handler
    else:
        final_handler = console_handler
    
    console_handler.addFilter(context_filter)
    
    if batch_logging:
        batch_handler = BatchHandler(
            target_handler=final_handler,
            capacity=batch_size,
            flush_interval=batch_interval
        )
        handlers = [batch_handler]
    else:
        handlers = [final_handler]

    if log_file:
        file_handler = CompressedRotatingFileHandler(
            log_file, maxBytes=512, backupCount=2
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        
        if batch_logging:
            file_batch_handler = BatchHandler(
                target_handler=file_handler,
                capacity=batch_size,
                flush_interval=batch_interval
            )
            handlers.append(file_batch_handler)
        else:
            handlers.append(file_handler)

    for handler in handlers:
        logger.addHandler(handler)

    return logger

def close_logger(logger: logging.Logger):
    global queue_listener
    
    for handler in logger.handlers[:]:
        try:
            handler.close()
        except Exception as e:
            print(f"Error closing handler: {e}")
        logger.removeHandler(handler)
    
    if queue_listener:
        queue_listener.stop()
        queue_listener = None
