import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a handler to write log messages to stderr
    handler = logging.StreamHandler(sys.stderr)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    # Check if the logger already has handlers to avoid duplication
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# Configure a default logger for the 'ace' package
get_logger('ace')
