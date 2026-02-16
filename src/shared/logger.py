import logging


def setup_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
