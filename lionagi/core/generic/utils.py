from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
from lion_core.generic.component import Component
from lionfuncs import to_dict, to_json


def from_obj(
    cls: type[Component],
    obj: Any,
    /,
    handle_how: Literal["suppress", "raise", "coerce", "coerce_key"] = "raise",
    fuzzy_parse: bool = False,
) -> Component | list[Component]:

    if isinstance(obj, pd.DataFrame):
        obj = [i for _, i in obj.iterrows()]

    def _obj_to_dict(obj_: Any, /) -> dict:

        dict_ = None

        if isinstance(obj_, dict):
            return obj_

        fp = None
        if isinstance(obj_, str):
            try:
                fp = Path(obj_)
            except Exception:
                pass
        fp = fp or obj_
        if isinstance(fp, Path):
            suffix = fp.suffix
            if suffix in cls.list_adapters():
                return cls.adapt_from(obj_, suffix)

        if isinstance(obj_, str):
            if "{" in obj_ or "}" in obj_:
                dict_ = to_json(obj_, fuzzy_parse=fuzzy_parse)
            if isinstance(dict_, list | dict):
                return dict_
            else:
                msg = obj_[:100] + "..." if len(obj_) > 100 else obj_
                raise ValueError(
                    f"The value input cannot be converted to a valid dict: {msg}"
                )

        dict_ = to_dict(obj_, suppress=True)
        if obj_ and not dict_:
            raise ValueError(f"Unsupported object type: {type(obj)}")
        return dict_

    def _dispatch_from_obj(
        obj_: Any,
        /,
        handle_how: Literal[
            "suppress", "raise", "coerce", "coerce_key"
        ] = "raise",
    ) -> Component:
        try:
            type_ = (
                str(type(obj_))
                .strip("_")
                .strip("<")
                .strip(">")
                .strip(".")
                .lower()
            )

            if "langchain" in type_:
                return cls.adapt_from(obj_, "langchain_doc")

            if "llamaindex" in type_:
                return cls.adapt_from(obj_, "llama_index_node")

            if "pandas" in type_ and "series" in type_:
                return cls.adapt_from(obj_, "pd_series")

            obj_ = _obj_to_dict(obj_)
            return cls.from_dict(obj_)

        except Exception as e:
            if handle_how == "raise":
                raise e
            if handle_how == "coerce":
                return cls.from_dict({"content": obj_})
            if handle_how == "suppress":
                return None
            if handle_how == "coerce_key":
                return cls.from_dict({str(k): v for k, v in obj_.items()})

    if isinstance(obj, (list, tuple)) and len(obj) > 1:
        return [_dispatch_from_obj(i, handle_how=handle_how) for i in obj]
    return _dispatch_from_obj(obj, handle_how=handle_how)
