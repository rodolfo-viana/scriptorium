import logging
import json
import queue
import threading
from logging.handlers import QueueHandler, QueueListener
from rich.logging import RichHandler
from .handlers import CompressedRotatingFileHandler, CompressedTimedRotatingFileHandler

# JSON Formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)

# Asynchronous Logging Setup
log_queue = queue.Queue(-1)  # Unlimited queue size
queue_handler = QueueHandler(log_queue)
queue_listener = None  # Will be initialized later

def get_logger(name: str, structured: bool = True, color: bool = True, async_logging: bool = False, log_file: str = None) -> logging.Logger:
    global queue_listener

    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicate handlers
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            handler.close()  # Ensure handlers are closed before removing
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)

    handlers = []
    
    if async_logging:
        if not queue_listener:
            queue_listener = QueueListener(log_queue)
            queue_listener.start()
        handlers.append(queue_handler)

    console_handler = RichHandler() if color else logging.StreamHandler()
    formatter = JSONFormatter() if structured else logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_file:
        file_handler = CompressedRotatingFileHandler(
            log_file, maxBytes=512, backupCount=2  # Reduced size for testing
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    for handler in handlers:
        logger.addHandler(handler)

    return logger

def close_logger(logger: logging.Logger):
    """Close all handlers to release file locks."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
