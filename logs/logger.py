# Placeholder - Author: Antonio
import logging

def get_logger():
    logger = logging.getLogger('proxy')
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        logger.addHandler(ch)
    return logger