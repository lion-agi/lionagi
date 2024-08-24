from lion_core.setting import RetryConfig, LN_UNDEFINED
from .schema import RateLimitConfig, CachedConfig

DEFAULT_RATE_LIMIT_CONFIG = RateLimitConfig(
    schema_version="2024-0824",
    interval=60,
    interval_request=10_000,
    interval_token=2_000_000,
    refresh_time=0.5,
    concurrent_capacity=1000,
)

DEFAULT_CACHED_CONFIG = CachedConfig(
    schema_version="2024-0824",
    ttl=300,
    key=None,
    namespace=None,
    key_builder=None,
    skip_cache_func=lambda x: False,
    serializer=None,
    plugins=None,
    alias=None,
    noself=lambda x: False,
)

DEFAULT_RETRY_CONFIG = RetryConfig(
    schema_version="2024-0824",
    num_retries=2,
    initial_delay=0,
    retry_delay=1,
    backoff_factor=2,
    retry_default=LN_UNDEFINED,
    retry_timeout=180,
    retry_timing=False,
    verbose_retry=True,
    error_msg=None,
    error_map=None,
)
