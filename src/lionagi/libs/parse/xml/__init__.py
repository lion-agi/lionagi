"""XML parsing and conversion utilities."""

from .convert import dict_to_xml, xml_to_dict
from .parser import XMLParser

__all__ = [
    "dict_to_xml",
    "xml_to_dict",
    "XMLParser",
]
