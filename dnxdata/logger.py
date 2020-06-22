import logging
import os

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))


def info_streaming(msg, *args, **kwargs):
    header = "Metrics-Streaming => "
    logger.info(header + msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    header = "Metrics-Common => "
    logger.info(header + msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    header = "Metrics-Common => "
    logger.debug(header + msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    header = "Metrics-Common => "
    logger.error(header + msg, *args, **kwargs)
