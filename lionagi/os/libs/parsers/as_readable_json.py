from typing import Any
import json
from ..data_handlers import to_dict


def as_readable_json(input_: Any, /) -> str:
    try:
        dict_ = to_dict(input_)
        return json.dumps(dict_, indent=4) if isinstance(dict_, dict) else str(dict_)
    except Exception as e:
        raise ValueError(f"Could not convert given input to readable dict: {e}") from e
