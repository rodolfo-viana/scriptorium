# Scriptorium - Advanced Logging for Python

[![Tests on main branch](https://github.com/rodolfo-viana/scriptorium/actions/workflows/run-tests-on-main.yml/badge.svg?branch=main)](https://github.com/rodolfo-viana/scriptorium/actions/workflows/run-tests-on-main.yml)

## Overview
Scriptorium is a powerful logging library for Python that enhances the built-in `logging` module with:

- **Structured Logging** (JSON format with rich context support)
- **Colorized Logs** (improves readability in the console)
- **Log Rotation & Compression** (async compression with error handling)
- **Asynchronous Logging** (non-blocking log processing)
- **Batch Logging** (efficient handling of high-volume logs)
- **Context Management** (hierarchical context with automatic cleanup)
- **Error Resilience** (graceful handling of compression failures)

## Installation
To install Scriptorium, run:
```sh
pip install scriptorium
```
For development (includes testing and linting tools):
```sh
pip install -e .[dev]
```

## Usage

### Basic Logger
```python
from scriptorium.logger import get_logger

logger = get_logger("my_logger")
logger.info("Hello, Scriptorium!")
```

### Batch Logging for High Volume
```python
logger = get_logger(
    "batch_logger",
    batch_logging=True,
    batch_size=1000,  # Flush every 1000 records
    batch_interval=1.0  # Or every second, whichever comes first
)
for _ in range(10000):
    logger.info("High volume logging")
```

### Context-Aware Logging
```python
from scriptorium.logger import get_logger, log_context

logger = get_logger("context_logger")

with log_context(request_id="123", user="alice"):
    logger.info("User logged in")  # Includes context automatically
    with log_context(operation="update"):
        logger.info("Profile updated")  # Nested context
```

### Async Compression with Error Handling
```python
logger = get_logger(
    "rotating_logger",
    log_file="app.log",
    compression_level=9,  # Maximum compression
)
# Logs are compressed asynchronously with fallback handling
```

### Combined Features
```python
logger = get_logger(
    "production_logger",
    structured=True,  # JSON output
    color=True,      # Rich console output
    async_logging=True,
    batch_logging=True,
    log_file="app.log"
)
```

## Advanced Features

### Error Handling
- Graceful handling of compression failures
- Automatic cleanup of failed compression attempts
- Preservation of original logs on error

### Performance Optimization
- Asynchronous compression using thread pools
- Batched logging for high-volume scenarios
- Configurable batch sizes and intervals

### Context Management
- Hierarchical context support
- Automatic context cleanup
- Thread-safe context handling

## Development & Testing
To run tests:
```sh
pytest -v
```

## CI/CD Integration
Scriptorium includes **GitHub Actions** for automated testing. Every push or PR triggers a test run.

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| structured | bool | True | Enable JSON formatting |
| color | bool | True | Enable rich console output |
| async_logging | bool | False | Enable async logging |
| batch_logging | bool | False | Enable batch processing |
| batch_size | int | 1000 | Records per batch |
| batch_interval | float | 1.0 | Seconds between flushes |
| compression_level | int | 9 | GZIP compression level |

## License
MIT License

## Contributing
Pull requests are welcome! If you find an issue, open an issue or submit a PR.
