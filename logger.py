# Author: Antonio

import logging
import os

LOG_DIR = "logs"
LOG_FILE = "proxy.log"


def get_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger("ProxyLogger")
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )

    # file handler
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
    file_handler.setFormatter(formatter)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger