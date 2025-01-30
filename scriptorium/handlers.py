import logging
import gzip
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class CompressedRotatingFileHandler(RotatingFileHandler):
    """A rotating file handler that compresses old logs."""

    def doRollover(self):
        super().doRollover()
        old_log = self.baseFilename + ".1"
        if os.path.exists(old_log):
            with open(old_log, "rb") as f_in:
                with gzip.open(old_log + ".gz", "wb") as f_out:
                    f_out.writelines(f_in)
            os.remove(old_log)

class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """A time-based rotating file handler that compresses old logs."""

    def doRollover(self):
        super().doRollover()
        old_log = self.baseFilename + ".1"
        if os.path.exists(old_log):
            with open(old_log, "rb") as f_in:
                with gzip.open(old_log + ".gz", "wb") as f_out:
                    f_out.writelines(f_in)
            os.remove(old_log)
