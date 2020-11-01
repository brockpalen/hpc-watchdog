"""Logging configuration."""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Name the logger after the package.
logger = logging.getLogger(__package__)

# get GlobusTransfer Logger
gt_logger = logging.getLogger("GlobusTransfer")
gt_logger.setLevel(logging.WARNING)

# Set default level for all handlers
logger.setLevel(logging.INFO)

# stream / stderr handler
st_handler = logging.StreamHandler()
st_handler.setLevel(logging.DEBUG)

# Log file
log_path = Path(__file__).parent.parent / "log" / "hpc-watchdog.log"
file_handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=30)
file_handler.setLevel(logging.DEBUG)

# set stream log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
st_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(st_handler)
logger.addHandler(file_handler)
gt_logger.addHandler(st_handler)


def set_debug():
    """Set log level for handlers to DEBUG."""
    logger.setLevel(logging.DEBUG)


def set_gt_debug():
    """Set log level for handlers to DEBUG."""
    gt_logger.setLevel(logging.DEBUG)
