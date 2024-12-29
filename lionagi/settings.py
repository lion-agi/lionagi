from datetime import timezone

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

CHAT_IMODEL_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o",
    "base_url": "https://api.openai.com/v1",
    "endpoint": "chat/completions",
    "api_key": "OPENAI_API_KEY",
    "queue_capacity": 100,
    "capacity_refresh_time": 60,
    "interval": None,
    "limit_requests": None,
    "limit_tokens": None,
}

PARSE_IMODEL_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1",
    "endpoint": "chat/completions",
    "api_key": "OPENAI_API_KEY",
    "queue_capacity": 100,
    "capacity_refresh_time": 60,
    "interval": None,
    "limit_requests": None,
    "limit_tokens": None,
}


class Settings:

    class Config:
        TIMEZONE: timezone = timezone.utc

    class Action:
        CACHED_CONFIG: dict = CACHED_CONFIG

    class API:
        CACHED_CONFIG: dict = CACHED_CONFIG

    class iModel:
        CHAT: dict = CHAT_IMODEL_CONFIG
        PARSE: dict = PARSE_IMODEL_CONFIG
