from lionfuncs import to_dict

from lion_core.communication.action_request import ActionRequest
from lion_core.generic.note import note
from lion_core.session.msg_handlers.extract_request import (
    extract_action_request,
    extract_request_from_content_code_block,
    extract_request_plain_function_calling,
)


def create_action_request(response: str | dict) -> list[ActionRequest] | None:
    msg = note(**to_dict(response))

    content_ = None
    if str(msg.get(["content"], "")).strip().lower() == "none":
        content_ = extract_request_plain_function_calling(msg, suppress=True)
    elif a := msg.get(["content", "tool_uses"], None):
        content_ = a
    else:
        content_ = extract_request_from_content_code_block(msg)

    if content_:
        content_ = [content_] if isinstance(content_, dict) else content_
        return extract_action_request(content_)

    _content = to_dict(msg["content"], fuzzy_parse=True, suppress=True)

    if _content and isinstance(_content, dict):
        if "action_request" in _content:
            content_ = _content["action_request"]
        if isinstance(content_, str):
            content_ = to_dict(content_, fuzzy_parse=True, suppress=True)
        if isinstance(content_, dict):
            content_ = [content_]
        if isinstance(content_, list):
            return extract_action_request(content_)

    return None
