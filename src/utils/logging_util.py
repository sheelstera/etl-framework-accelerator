import logging

def setup_logger(name):
    """Setup a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
