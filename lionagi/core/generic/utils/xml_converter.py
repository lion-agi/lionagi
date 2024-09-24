from pathlib import Path
from typing import Any

from lion_core.generic import Component as CoreComponent
from lion_core.converter import Converter
from lionagi.libs import lionfuncs as ln
from lionagi.libs.sys_util import SysUtil


class XMLStringConverter(Converter):
    _object = "xml"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: str, **kwargs: Any) -> dict:
        kwargs["str_type"] = "xml"
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
        **kwargs: Any,
    ) -> Any:
        """kwargs for to_str"""
        return ln.to_str(
            subject, serialize_as="xml", parser_kwargs=convert_kwargs, **kwargs
        )


class XMLFileConverter(Converter):
    _object = "xml_file"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: str, **kwargs: Any) -> dict:
        kwargs["str_type"] = "xml"
        with open(object_, "r") as file:
            return ln.to_dict(file.read(), **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: CoreComponent, **kwargs: Any) -> dict:
        """kwargs for to_dict"""
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
        text = XMLStringConverter.to_obj(subject, convert_kwargs=convert_kwargs)
        filepath = filepath or SysUtil.create_path(**kwargs)
        with open(filepath, "w") as f:
            f.write(text)
