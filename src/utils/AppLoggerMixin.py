import logging
from wsgidav import util

class AppLoggerMixin(object):

    logger = None

    @classmethod
    def get_logger(cls):
        if cls.logger == None:
            cls.logger = util.get_module_logger(__name__)
            cls.logger.setLevel(logging.INFO)
        return cls.logger