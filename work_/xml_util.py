import xml.etree.ElementTree as ET

def add_element(xml_string: str, parent_tag: str, new_element: ET.Element) -> str:
    """
    Adds a new element to the XML string under the specified parent tag.

    Args:
        xml_string: The XML string to modify.
        parent_tag: The parent tag under which to add the new element.
        new_element: The Element to add.

    Returns:
        The modified XML string.

    Examples:
        >>> root = ET.Element('person')
        >>> name = ET.SubElement(root, 'name')
        >>> name.text = 'John'
        >>> new_element = ET.Element('age')
        >>> new_element.text = '30'
        >>> xml_str = ET.tostring(root, encoding='unicode')
        >>> modified_xml = add_element(xml_str, 'person', new_element)
        >>> print(modified_xml)
        '<person><name>John</name><age>30</age></person>'
    """
    root = ET.fromstring(xml_string)
    parent = root.find('.//' + parent_tag)
    if parent is not None:
        parent.append(new_element)
    return ET.tostring(root, encoding='unicode')
