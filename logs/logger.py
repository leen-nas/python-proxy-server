
#Author: Antonio


import logging
import os

LOG_DIR = "logs"
LOG_FILE = "proxy.log"


def get_logger():
    logger = logging.getLogger("proxy")

    # avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # create logs folder if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )

    # =========================
    # Console logging
    # =========================
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # =========================
    # File logging (THIS CREATES proxy.log)
    # =========================
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
    file_handler.setFormatter(formatter)

    # attach handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger