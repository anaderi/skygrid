import sys
import logging

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