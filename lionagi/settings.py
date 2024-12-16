from datetime import timezone
from enum import Enum

from lionagi.protocols.configs import (
    BranchConfig,
    LionIDConfig,
    MessageConfig,
    RetryConfig,
    TimedFuncCallConfig,
    iModelConfig,
)
from lionagi.protocols.configs.log_config import LogConfig


class BaseSystemFields(str, Enum):
    ln_id = "ln_id"
    TIMESTAMP = "timestamp"
    METADATA = "metadata"
    EXTRA_FIELDS = "extra_fields"
    CONTENT = "content"
    CREATED = "created"
    EMBEDDING = "embedding"


DEFAULT_ID_CONFIG = LionIDConfig(
    n=36,
    random_hyphen=True,
    num_hyphens=4,
    hyphen_start_index=6,
    hyphen_end_index=-6,
    prefix="ao",
    postfix="",
)

DEFAULT_TIMED_FUNC_CALL_CONFIG = TimedFuncCallConfig(
    initial_delay=0,
    retry_timeout=None,
    retry_timing=False,
    error_msg=None,
    error_map=None,
)

DEFAULT_RETRY_CONFIG = RetryConfig(
    num_retries=0,
    initial_delay=0,
    retry_delay=0,
    backoff_factor=1,
    retry_timeout=None,
    retry_timing=False,
    verbose_retry=False,
    error_msg=None,
    error_map=None,
)


DEFAULT_CHAT_CONFIG = iModelConfig(
    provider="openai",
    task="chat",
    model="gpt-4o",
    api_key="OPENAI_API_KEY",
)


DEFAULT_RETRY_iMODEL_CONFIG = iModelConfig(
    provider="openai",
    task="chat",
    model="gpt-4o-mini",
    api_key="OPENAI_API_KEY",
)


DEFAULT_MESSAGE_CONFIG = MessageConfig(
    validation_mode="raise",
    auto_retries=False,
    max_retries=0,
    allow_actions=True,
    auto_invoke_action=True,
)


DEFAULT_MESSAGE_LOG_CONFIG = LogConfig(
    persist_dir="./data/logs",
    subfolder="messages",
    file_prefix="message_",
    capacity=128,
    auto_save_on_exit=True,
    clear_after_dump=True,
    use_timestamp=True,
    extension=".csv",
)

DEFAULT_ACTION_LOG_CONFIG = LogConfig(
    persist_dir="./data/logs",
    subfolder="actions",
    file_prefix="action_",
    capacity=128,
    auto_save_on_exit=True,
    clear_after_dump=True,
    use_timestamp=True,
    extension=".csv",
)

DEFAULT_BRANCH_CONFIG = BranchConfig(
    name=None,
    user=None,
    message_log_config=DEFAULT_MESSAGE_LOG_CONFIG,
    action_log_config=DEFAULT_ACTION_LOG_CONFIG,
    message_config=DEFAULT_MESSAGE_CONFIG,
    auto_register_tools=True,
    action_call_config=DEFAULT_TIMED_FUNC_CALL_CONFIG,
    imodel_config=DEFAULT_CHAT_CONFIG,
    retry_imodel_config=DEFAULT_RETRY_iMODEL_CONFIG,
)


DEFAULT_TIMEZONE = timezone.utc
BASE_LION_FIELDS = set(BaseSystemFields.__members__.values())


class Settings:

    class Config:
        ID: LionIDConfig = DEFAULT_ID_CONFIG
        RETRY: RetryConfig = DEFAULT_RETRY_CONFIG
        TIMED_CALL: TimedFuncCallConfig = DEFAULT_TIMED_FUNC_CALL_CONFIG
        TIMEZONE: timezone = DEFAULT_TIMEZONE

    class Branch:
        BRANCH: BranchConfig = DEFAULT_BRANCH_CONFIG

    class iModel:
        CHAT: dict = {"model": "openai/gpt-4o"}
        PARSE: iModelConfig = DEFAULT_CHAT_CONFIG


# File: autoos/setting.py
