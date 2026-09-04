import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(__file__).parent / 'sms-sender.log'

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(filename)s %(funcName)s: %(message)s'
        ))
        logger.addHandler(handler)
    return logger
