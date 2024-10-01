from lion_core import LogManager

event_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="events",
    file_prefix="event_",
)

message_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="messages",
    file_prefix="message_",
)

form_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="forms",
    file_prefix="form_",
)

__all__ = [
    "event_log_manager",
    "message_log_manager",
    "form_log_manager",
]
