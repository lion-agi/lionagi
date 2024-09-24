from __future__ import annotations

import json


import json
from pathlib import Path
from typing import Any

from lion_core.generic import Component as CoreComponent
from lion_core.converter import Converter
from lionagi.libs import lionfuncs as ln
from lionagi.libs.sys_util import SysUtil


class JsonStringConverter(Converter):
    """JSON converter implementation."""

    _object = "json"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: str, **kwargs: Any) -> dict:
        """Convert a JSON string to a dictionary.

        Args:
            object_: JSON string to convert.
            **kwargs: Additional arguments for json.loads.

        Returns:
            A dictionary representation of the JSON string.
        """
        kwargs["str_type"] = "json"
        return ln.to_dict(object_, **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: CoreComponent, **kwargs: Any) -> dict:
        """Convert a subject to a dictionary.

        Args:
            subject: The subject to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the subject.
        """
        return subject.to_dict(**kwargs)

    @classmethod
    def to_obj(
        cls,
        subject: CoreComponent,
        *,
        convert_kwargs: dict = {},
        **kwargs: Any,
    ) -> Any:
        """Convert a subject to a JSON string.

        Args:
            subject: The subject to convert.
            convert_kwargs: Kwargs for convert_sub_to_obj_dict.
            **kwargs: Additional arguments for json.dumps.

        Returns:
            A JSON string representation of the subject.
        """
        _dict = cls.convert_sub_to_obj_dict(subject=subject, **convert_kwargs)
        return json.dumps(obj=_dict, **kwargs)


class JsonFileConverter(Converter):
    _object = "json_file"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: str | Path, **kwargs: Any) -> dict:
        object_ = json.load(object_)
        return ln.to_dict(object_, **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: CoreComponent, **kwargs: Any) -> dict:
        return ln.to_dict(subject, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subject: CoreComponent,
        *,
        convert_kwargs: dict = {},
        filepath=None,
        **kwargs: Any,
    ) -> Any:
        """kwargs for create_path"""
        text = JsonStringConverter.to_obj(subject, convert_kwargs=convert_kwargs)
        filepath = filepath or SysUtil.create_path(**kwargs)
        with open(filepath, "w") as f:
            f.write(text)
