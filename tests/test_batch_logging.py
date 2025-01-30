import logging
import pytest
import time
import threading
import json
from scriptorium.logger import get_logger, close_logger, JSONFormatter, BatchHandler

def get_json_from_record(record, logger):
    for handler in logger.handlers:
        if isinstance(handler.formatter, JSONFormatter):
            return json.loads(handler.formatter.format(record))
    raise ValueError("No JSON formatter found")

@pytest.fixture
def batch_logger():
    logger = get_logger("test_batch", batch_logging=True, batch_size=5, 
                       batch_interval=0.5, structured=True)
    try:
        yield logger
    finally:
        close_logger(logger)

def wait_for_logs(caplog, expected_count, timeout=2.0, check_messages=None, logger=None):
    def get_messages():
        if not logger or not logger.handlers:
            return [r.message for r in caplog.records]
        
        formatter = None
        for handler in logger.handlers:
            if isinstance(handler.formatter, JSONFormatter):
                formatter = handler.formatter
                break
        
        if not formatter:
            return [r.message for r in caplog.records]
            
        return [json.loads(formatter.format(r))["message"] for r in caplog.records]
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if len(caplog.records) >= expected_count:
            if check_messages is None:
                return True
            
            messages = get_messages()
            if all(msg in messages for msg in check_messages):
                return True
                
        time.sleep(0.1)
    return False

@pytest.fixture(autouse=True)
def clear_caplog(caplog):
    caplog.clear()
    yield

class MockHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
        self._lock = threading.Lock()
    
    def emit(self, record):
        with self._lock:
            self.records.append(record)
    
    def clear(self):
        with self._lock:
            self.records.clear()

@pytest.fixture
def test_handler():
    handler = MockHandler()
    yield handler
    handler.clear()

def test_batch_logging_size(batch_logger, test_handler, caplog):
    for handler in batch_logger.handlers:
        if isinstance(handler, BatchHandler):
            handler.target_handler = test_handler
            break
    
    expected_messages = [f"Message {i}" for i in range(4)] + ["Final message"]
    
    for msg in expected_messages[:-1]:
        batch_logger.info(msg)
        time.sleep(0.1)
    
    assert len(test_handler.records) == 0, \
        "Messages were processed before batch was full"
    
    batch_logger.info(expected_messages[-1])
    
    start_time = time.time()
    while time.time() - start_time < 2.0:
        if len(test_handler.records) == 5:
            break
        time.sleep(0.1)
    
    assert len(test_handler.records) == 5, "Not all messages were processed"
    messages = [r.getMessage() for r in test_handler.records]
    assert messages == expected_messages, "Messages were not processed in order"

def test_batch_logging_interval(batch_logger, test_handler):
    for handler in batch_logger.handlers:
        if isinstance(handler, BatchHandler):
            handler.target_handler = test_handler
            break
    
    expected_messages = [f"Message {i}" for i in range(3)]
    
    for msg in expected_messages:
        batch_logger.info(msg)
    
    start_time = time.time()
    while time.time() - start_time < 2.0:
        if len(test_handler.records) == 3:
            break
        time.sleep(0.1)
    
    assert len(test_handler.records) == 3, "Not all messages were flushed"
    messages = [r.getMessage() for r in test_handler.records]
    assert messages == expected_messages, "Messages were not processed in order"

def test_batch_logging_with_async(test_handler):
    logger = get_logger("test_batch_async", 
                       batch_logging=True, 
                       async_logging=True,
                       batch_size=5,
                       structured=True)
    
    for handler in logger.handlers:
        if isinstance(handler, BatchHandler):
            handler.target_handler = test_handler
            break
    
    expected_messages = [f"Async batch message {i}" for i in range(5)]
    
    try:
        for msg in expected_messages:
            logger.info(msg)
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            if len(test_handler.records) == 5:
                break
            time.sleep(0.1)
        
        assert len(test_handler.records) == 5, "Not all messages were processed"
        messages = [r.getMessage() for r in test_handler.records]
        assert messages == expected_messages, "Messages were not processed in order"
    finally:
        close_logger(logger)

def test_batch_handler_cleanup(test_handler):
    logger = get_logger("test_cleanup", 
                       batch_logging=True,
                       batch_size=10,
                       batch_interval=1.0,
                       structured=True)
    
    for handler in logger.handlers:
        if isinstance(handler, BatchHandler):
            handler.target_handler = test_handler
            break
    
    messages = ["Message 1", "Message 2", "Message 3"]
    
    for msg in messages:
        logger.info(msg)
    
    close_logger(logger)
    
    assert len(test_handler.records) == 3, "Not all messages were flushed on close"
    actual_messages = [r.getMessage() for r in test_handler.records]
    assert actual_messages == messages, "Messages were not processed in order"
