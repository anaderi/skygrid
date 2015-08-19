import sys
import logging
from config import config
from raven import Client

def default_logger():
    logger = logging.getLogger("default")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(processName)s\t%(message)s')
        handler.setFormatter(formatter)
    return logger

logger = default_logger()


sentry_client = None
capture_exception = lambda: None

if getattr(config, "SENTRY_KEY", None):
    logger.debug("Setting sentry client")
    sentry_client = Client(config.SENTRY_KEY)
    capture_exception = sentry_client.captureException
