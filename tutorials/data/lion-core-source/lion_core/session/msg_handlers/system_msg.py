from typing import Any

from lionfuncs import LN_UNDEFINED

from lion_core.communication.message import MessageFlag
from lion_core.communication.system import System


def handle_system(
    system: Any,
    sender: Any | MessageFlag,
    recipient: Any | MessageFlag,
    system_datetime: bool | str | None | MessageFlag,
):
    if isinstance(system, System):
        return system

    if system:
        return System(
            system=system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
        )


def validate_system(
    system: Any = None,
    sender=None,
    recipient=None,
    system_datetime=None,
) -> System:
    config = {
        "sender": sender,
        "recipient": recipient,
        "system_datetime": system_datetime,
    }
    config = {k: v for k, v in config.items() if v not in [None, LN_UNDEFINED]}

    if not system:
        return System(DEFAULT_SYSTEM, **config)
    if isinstance(system, System):
        if config:
            for k, v in config.items():
                setattr(system, k, v)
        return system
    return System(system, **config)


DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."
