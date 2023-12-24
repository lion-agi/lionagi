import logging
from abc import ABC, abstractmethod

import logging
import logging.config

# Global logging setup
def setup_global_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s')


# BaseLogger for centralized logger creation
class BaseLogger:
    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

