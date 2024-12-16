import xml.etree.ElementTree as ET
from typing import Any

from .parser import XMLParser


def xml_to_dict(
    xml_string: str,
    /,
    suppress=False,
    remove_root: bool = True,
    root_tag: str = None,
) -> dict[str, Any]:
    """
    Parse an XML string into a nested dictionary structure.

    This function converts an XML string into a dictionary where:
    - Element tags become dictionary keys
    - Text content is assigned directly to the tag key if there are no children
    - Attributes are stored in a '@attributes' key
    - Multiple child elements with the same tag are stored as lists

    Args:
        xml_string: The XML string to parse.

    Returns:
        A dictionary representation of the XML structure.

    Raises:
        ValueError: If the XML is malformed or parsing fails.
    """
    try:
        a = XMLParser(xml_string).parse()
        if remove_root and (root_tag or "root") in a:
            a = a[root_tag or "root"]
        return a
    except ValueError as e:
        if not suppress:
            raise e


def dict_to_xml(data: dict, /, root_tag: str = "root") -> str:

    root = ET.Element(root_tag)

    def convert(dict_obj: dict, parent: Any) -> None:
        for key, val in dict_obj.items():
            if isinstance(val, dict):
                element = ET.SubElement(parent, key)
                convert(dict_obj=val, parent=element)
            else:
                element = ET.SubElement(parent, key)
                element.text = str(object=val)

    convert(dict_obj=data, parent=root)
    return ET.tostring(root, encoding="unicode")
