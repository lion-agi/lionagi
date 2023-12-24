import logging
from abc import ABC, abstractmethod

import logging
import logging.config
import os

# Global logging setup
def setup_global_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s')


# BaseLogger for centralized logger creation
class BaseLogger:
    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

# BaseTool class with integrated logging
class BaseTool(ABC):
    def __init__(self):
        self.logger = BaseLogger.get_logger(self.__class__.__name__)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass
    
# Basic configuration for the logging system
def setup_logging():
    logging_conf = {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": logging.INFO,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": logging.INFO,
        },
    }

    logging.config.dictConfig(logging_conf)


# Call this at the start of your application
setup_global_logging()


setup_logging()