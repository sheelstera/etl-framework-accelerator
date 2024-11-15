# decorators/logger_decorator.py
from functools import wraps
import logging

def log_method(func):
    """Decorator that logs method entry, exit, and any exceptions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Entering {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} with result: {result}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper
