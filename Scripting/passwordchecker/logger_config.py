import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(__file__).parent / 'checkpassword.log'

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'
            ))
        logger.addHandler(handler)
    return logger


