import logging
import pytest
import json
import os
from scriptorium.logger import get_logger, close_logger, log_context, JSONFormatter
from scriptorium.handlers import CompressionError

@pytest.fixture
def json_logger():
    logger = get_logger("test_context", structured=True)
    yield logger
    close_logger(logger)

def get_json_from_record(record, logger):
    for handler in logger.handlers:
        if isinstance(handler.formatter, JSONFormatter):
            return json.loads(handler.formatter.format(record))
    raise ValueError("No JSON formatter found")

def test_log_context(json_logger, caplog):
    with caplog.at_level(logging.INFO):
        with log_context(user_id="123", request_id="abc"):
            json_logger.info("User action")
            
        log_record = get_json_from_record(caplog.records[0], json_logger)
        assert log_record["context"] == {}
        assert log_record["user_id"] == "123"
        assert log_record["request_id"] == "abc"

def test_nested_context(json_logger, caplog):
    with caplog.at_level(logging.INFO):
        with log_context(outer="value"):
            json_logger.info("Outer message")
            with log_context(inner="nested"):
                json_logger.info("Inner message")
            json_logger.info("Back to outer")

        records = [get_json_from_record(r, json_logger) for r in caplog.records]
        
        assert records[0]["outer"] == "value"
        assert "inner" not in records[0]
        
        assert records[1]["outer"] == "value"
        assert records[1]["inner"] == "nested"
        
        assert records[2]["outer"] == "value"
        assert "inner" not in records[2]

def test_exception_logging(json_logger, caplog):
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("Test error")
        except ValueError:
            json_logger.exception("An error occurred")

        log_record = get_json_from_record(caplog.records[0], json_logger)
        assert "exception" in log_record
        assert "ValueError: Test error" in log_record["exception"]

def test_compression_error_handling(tmp_path):
    log_file = tmp_path / "test.log"
    logger = get_logger("test_errors", log_file=str(log_file))

    for _ in range(5000):
        logger.info("Test message")

    assert os.path.exists(log_file)
    
    close_logger(logger)

    backup_log = str(log_file) + ".1"
    compressed_log = backup_log + ".gz"
    assert os.path.exists(compressed_log) or os.path.exists(backup_log)

def test_context_cleanup(json_logger, caplog):
    with caplog.at_level(logging.INFO):
        try:
            with log_context(test="value"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        json_logger.info("After error")
        log_record = get_json_from_record(caplog.records[0], json_logger)
        assert "test" not in log_record
