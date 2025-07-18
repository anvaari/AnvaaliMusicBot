import logging
import sys
from config import app_config


def get_logger(module_name):
    """
    Config logger to follow up steps
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(app_config.LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s at line: %(lineno)d  - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
