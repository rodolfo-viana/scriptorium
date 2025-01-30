import logging
import os
import gzip
import pytest
import time
from scriptorium.logger import get_logger, close_logger
from scriptorium.handlers import CompressedRotatingFileHandler

LOG_FILE = "test.log"

@pytest.fixture(autouse=True)
def cleanup():
    yield
    
    time.sleep(0.5)

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    rotated_log = LOG_FILE + ".1.gz"
    if os.path.exists(rotated_log):
        os.remove(rotated_log)

def test_log_rotation():
    logger = get_logger("test_rotation", log_file=LOG_FILE)
    
    for _ in range(5000):
        logger.info("This is a test log entry")

    time.sleep(0.5)

    close_logger(logger)

    assert os.path.exists(LOG_FILE), "Log file was not created"
    
    rotated_log = LOG_FILE + ".1.gz"
    assert os.path.exists(rotated_log), f"Rotated log file {rotated_log} not found"

def test_compressed_log_integrity():
    logger = get_logger("test_rotation", log_file=LOG_FILE)

    for _ in range(5000):
        logger.info("This is a test log entry")

    time.sleep(0.5)
    
    close_logger(logger)

    rotated_log = LOG_FILE + ".1.gz"
    assert os.path.exists(rotated_log), f"Compressed log file {rotated_log} does not exist"

    with gzip.open(rotated_log, "rt") as f:
        content = f.read()

    assert "This is a test log entry" in content, "Expected log message not found in compressed log"
