import logging
import sys
from ace.config import get_config

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name.

    This function provides a centralized way to configure and access loggers
    throughout the application. It ensures that all loggers share a consistent
    formatting and logging level, which can be customized in the application's
    configuration.

    The logger is configured to output messages to the standard output, making
    it easy to monitor the application's behavior in different environments,
    including local development, testing, and production.

    Usage:
        To use the logger in any module, simply import this function and call
        it with the module's name:

        from ace.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is an informational message.")
        logger.warning("This is a warning message.")

    Args:
        name (str): The name of the logger, typically the module's `__name__`.

    Returns:
        logging.Logger: A configured logger instance.
    """
    log_level_str = get_config().get('log_level', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
