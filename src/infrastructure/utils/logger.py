import logging
import os.path

from src.infrastructure.data_access.environment import Environment

def setup_logger(name, log_filename, level=logging.INFO):
    log_dir = Environment.get_log_dir()
    filepath = os.path.join(log_dir, log_filename)
    handler = logging.FileHandler(filepath)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
