import logging
import gzip
import os
import shutil
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

class CompressionError(Exception):
    pass

def compress_file(source: str, target: str, compression_level: int = 9) -> None:
    try:
        with open(source, "rb") as f_in:
            with gzip.open(target, "wb", compresslevel=compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as e:
        raise CompressionError(f"Failed to compress {source} to {target}: {str(e)}")

class BaseCompressedHandler:
    
    def __init__(self, compression_level: int = 9, max_workers: int = 4):
        self.compression_level = compression_level
        self._compress_executor = ThreadPoolExecutor(max_workers=max_workers)
        self._compression_errors: list = []
    
    def _compress_async(self, source: str) -> None:
        target = source + ".gz"
        try:
            compress_file(source, target, self.compression_level)
            os.remove(source)
        except CompressionError as e:
            self._compression_errors.append(str(e))
            if os.path.exists(target):
                os.remove(target)

class CompressedRotatingFileHandler(RotatingFileHandler, BaseCompressedHandler):

    def __init__(self, filename: str, mode: str = "a", maxBytes: int = 0,
                 backupCount: int = 0, encoding: Optional[str] = None,
                 delay: bool = False, compression_level: int = 9,
                 max_workers: int = 4):
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount,
                                   encoding, delay)
        BaseCompressedHandler.__init__(self, compression_level, max_workers)

    def doRollover(self) -> None:
        super().doRollover()
        old_log = self.baseFilename + ".1"
        if os.path.exists(old_log):
            self._compress_executor.submit(self._compress_async, old_log)

    def close(self) -> None:
        self._compress_executor.shutdown(wait=True)
        super().close()

class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler, BaseCompressedHandler):

    def __init__(self, filename: str, when: str = "h", interval: int = 1,
                 backupCount: int = 0, encoding: Optional[str] = None,
                 delay: bool = False, utc: bool = False, atTime: Optional[object] = None,
                 compression_level: int = 9, max_workers: int = 4):
        TimedRotatingFileHandler.__init__(self, filename, when, interval,
                                        backupCount, encoding, delay, utc, atTime)
        BaseCompressedHandler.__init__(self, compression_level, max_workers)

    def doRollover(self) -> None:
        super().doRollover()
        old_log = self.baseFilename + ".1"
        if os.path.exists(old_log):
            self._compress_executor.submit(self._compress_async, old_log)

    def close(self) -> None:
        self._compress_executor.shutdown(wait=True)
        super().close()
