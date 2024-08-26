from pathlib import Path
from typing import Any

from lionagi.os import Converter, lionfuncs as ln, SysUtil


class XMLStringConverter(Converter):

    ET = SysUtil.import_module(
        package_name="xml",
        module_name="etree.ElementTree",
    )

    @staticmethod
    def from_obj(cls, obj: str, **kwargs) -> dict:
        return ln.to_dict(obj, str_type="xml", **kwargs)

    @staticmethod
    def to_obj(self, **kwargs) -> str:
        """Convert the component to an XML string."""

        root = XMLStringConverter.ET.Element(self.__class__.__name__)

        def convert(dict_obj: dict, parent: Any) -> None:
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = XMLStringConverter.ET.SubElement(parent, key)
                    convert(dict_obj=val, parent=element)
                else:
                    element = XMLStringConverter.ET.SubElement(parent, key)
                    element.text = str(object=val)

        convert(dict_obj=ln.to_dict(self, **kwargs), parent=root)
        return XMLStringConverter.ET.tostring(root, encoding="unicode")


class XMLFileConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: str | Path, **kwargs) -> dict:
        return ln.to_dict(SysUtil.read_file(obj), str_type="xml", **kwargs)

    @staticmethod
    def to_obj(
        self,
        persist_path: str | Path,
        path_kwargs={},
        **kwargs,
    ):
        text = XMLStringConverter.to_obj(self=self, **kwargs)
        path_kwargs = SysUtil._get_path_kwargs(
            persist_path=persist_path,
            postfix="xml",
            **path_kwargs,
        )
        SysUtil.save_to_file(text=text, **path_kwargs)
