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
captureException = lambda: None

if config.SENTRY_KEY:
    logger.debug("Setting sentry client")
    sentry_client = Client(config.SENTRY_KEY)
    captureException = sentry_client.captureException
