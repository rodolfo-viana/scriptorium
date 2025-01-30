# Scriptorium - Advanced Logging for Python

## Overview
Scriptorium is a powerful logging library for Python that enhances the built-in `logging` module with:

- **Structured Logging** (JSON format for better parsing)
- **Colorized Logs** (improves readability in the console)
- **Log Rotation & Compression** (prevents large log files from filling up disk space)
- **Asynchronous Logging** (improves performance by handling logs in the background)
- **Context-aware Logging** (includes request/session IDs for better tracing)

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

### Log Rotation & Compression
```python
logger = get_logger("rotating_logger", log_file="app.log")
for _ in range(1000):
    logger.info("This log will be rotated and compressed")
```

### Asynchronous Logging
```python
logger = get_logger("async_logger", async_logging=True)
logger.info("This log is processed asynchronously!")
```

## Development & Testing
To run tests:
```sh
pytest -v
```

## CI/CD Integration
Scriptorium includes **GitHub Actions** for automated testing. Every push or PR triggers a test run.

## License
MIT License

## Contributing
Pull requests are welcome! If you find an issue, open an issue or submit a PR.

