import logging
from os import getenv

LOGGER = None
if LOGGER is None:
    LOGGER = logging.getLogger("bs.log")
    LOGGER.setLevel(getenv("BS_LOG_LEVEL", "INFO"))


def log(*args, **kwargs):
    """Pass-through to the global LOGGER objects log method."""
    LOGGER.log(*args, **kwargs)


def info(*args, **kwargs):
    """Pass-through to the global LOGGER objects info method."""
    LOGGER.info(*args, **kwargs)


def critical(*args, **kwargs):
    """Pass-through to the global LOGGER objects critical method."""
    LOGGER.critical(*args, **kwargs)


def exception(*args, **kwargs):
    """Pass-through to the global LOGGER objects exception method."""
    LOGGER.exception(*args, **kwargs)


def warning(*args, **kwargs):
    """Pass-through to the global LOGGER objects warning method."""
    LOGGER.warning(*args, **kwargs)


def debug(*args, **kwargs):
    """Pass-through to the global LOGGER objects debug method."""
    LOGGER.debug(*args, **kwargs)
