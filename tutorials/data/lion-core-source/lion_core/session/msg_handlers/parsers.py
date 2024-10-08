import re

from lionfuncs import extract_json_block, md_to_json, to_dict

from lion_core.generic.note import note

identifier = [
    "tool_uses",
    "actions",
    "action",
    "action_request",
]

_patterns = {
    "json": {
        "tool_uses": r"```json\n({.*?tool_uses.*?})\n```",
        "actions": r"```json\n({.*?actions.*?})\n```",
        "action": r"```json\n({.*?action.*?})\n```",
        "action_request": r"```json\n({.*?action_request.*?})\n```",
    },
    "xml": {
        "tool_uses": r"<tool_uses>(.*?)</tool_uses>",
        "actions": r"<actions>(.*?)</actions>",
        "action": r"<action>(.*?)</action>",
        "action_request": r"<action_request>(.*?)</action_request>",
    },
}
patterns = note(**_patterns)


def _force_parse_json(s_: str) -> tuple:
    for idx, i in enumerate(identifier):
        cp = ["json", i]
        match = re.search(patterns[cp], s_, re.DOTALL)
        action_block = match.group(1) if match else None

        if action_block is not None:
            out = to_dict(
                s_,
                str_type="json",
                parser=md_to_json,
                suppress=True,
            )
            if not out:
                out = to_dict(
                    s_,
                    str_type="json",
                    fuzzy_parse=True,
                    suppress=True,
                )
            if not out:
                out = to_dict(
                    s_,
                    str_type="json",
                    parser=extract_json_block,
                    suppress=True,
                )
            if out and isinstance(out, dict):
                return idx, out
    return None, None


def _force_parse_xml(s_: str) -> tuple:
    for idx, i in enumerate(identifier):
        cp = ["xml", i]

        match = re.search(patterns[cp], s_, re.DOTALL)
        action_block = match.group(1) if match else None
        if action_block is not None:
            out = to_dict(
                action_block,
                str_type="xml",
                suppress=True,
            )
            if out is not None and isinstance(out, dict):
                return idx, out
    return None, None


def _parse_to_action_block(s_: str):
    if "json" in s_:
        idx, i = _force_parse_json(s_)
        if i is None:
            idx, i = _force_parse_json(s_.replace("'", '"'))
        if i is not None and identifier[idx] in i:
            return i[identifier[idx]]

    idx, i = _force_parse_xml(s_)
    if i is not None and identifier[idx] in i:
        return i[identifier[idx]]
