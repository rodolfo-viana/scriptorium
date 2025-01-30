import logging
import pytest
import time
from scriptorium.logger import get_logger

@pytest.fixture
def async_logger():
    return get_logger("test_async", async_logging=True)

def test_async_logging(async_logger, caplog):
    """Ensure async logging works correctly."""
    with caplog.at_level(logging.INFO):
        async_logger.info("Async log test")
    
    time.sleep(0.5)
    assert "Async log test" in caplog.text
