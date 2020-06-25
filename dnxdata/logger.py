import logging
import os


class Logger:

    def __init__(self, header):
        self.header = header
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

    def info(self, msg, *args, **kwargs):
        self.logger.info(self.header + msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self.header + msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self.header + msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self.header + msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self.header + msg, *args, **kwargs)
