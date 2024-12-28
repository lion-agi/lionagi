from .utils import UNDEFINED, RCallParams

CACHED_CONFIG = {
    "ttl": 300,
    "key": None,
    "namespace": None,
    "key_builder": None,
    "skip_cache_func": lambda x: False,
    "serializer": None,
    "plugins": None,
    "alias": None,
    "noself": lambda x: False,
}

ACTION_RETRY_CONFIG = {
    "num_retries": 0,
    "initial_delay": 0,
    "retry_delay": 0,
    "backoff_factor": 1,
    "retry_default": UNDEFINED,
    "retry_timeout": None,
    "retry_timing": False,
    "verbose_retry": True,
}

API_RETRY_CONFIG = {
    "num_retries": 2,
    "initial_delay": 0,
    "retry_delay": 1,
    "backoff_factor": 2,
    "retry_default": UNDEFINED,
    "retry_timeout": None,
    "retry_timing": False,
    "verbose_retry": True,
}


class Settings:

    class Action:
        CACHED_CONFIG: dict = CACHED_CONFIG
        RETRY_CONFIG: dict = ACTION_RETRY_CONFIG

    class API:
        CACHED_CONFIG: dict = CACHED_CONFIG
        RETRY_CONFIG: dict = API_RETRY_CONFIG
