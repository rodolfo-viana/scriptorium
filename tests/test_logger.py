import pytest
import logging
from scriptorium.logger import get_logger

def test_logger_basic():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)

def test_logger_logs_message(caplog):
    logger = get_logger("test_logger")
    with caplog.at_level(logging.INFO):
        logger.info("This is a test log")
    
    assert "This is a test log" in caplog.text
