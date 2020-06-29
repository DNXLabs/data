import logging
from dnxdata.utils.environments import LOG_LEVEL


class Logger:

    def __init__(self, header):
        self.header = str(header)
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)

    def info(self, msg, *args, **kwargs):
        msg = "{} {}".format(self.header, msg)
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        msg = "{} {}".format(self.header, msg)
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg = "{} {}".format(self.header, msg)
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg = "{} {}".format(self.header, msg)
        self.logger.warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg = "{} {}".format(self.header, msg)
        self.logger.critical(msg, *args, **kwargs)
