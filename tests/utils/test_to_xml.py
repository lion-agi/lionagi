from lionagi.utils import to_xml


def test_simple_dict():
    data = {"a": 1, "b": "hello"}
    xml = to_xml(data, root_name="data")
    assert xml == "<data><a>1</a><b>hello</b></data>"


def test_nested_dict():
    data = {
        "person": {
            "name": "Alice",
            "age": 30,
            "address": {"city": "Wonderland", "zip": "12345"},
        }
    }
    xml = to_xml(data, root_name="root")
    expected = (
        "<root>"
        "<person>"
        "<name>Alice</name>"
        "<age>30</age>"
        "<address>"
        "<city>Wonderland</city>"
        "<zip>12345</zip>"
        "</address>"
        "</person>"
        "</root>"
    )
    assert xml == expected


def test_list_values():
    data = {"items": [10, 20, 30]}
    xml = to_xml(data, root_name="root")
    # Each item should repeat the <items> tag
    expected = (
        "<root><items>10</items><items>20</items><items>30</items></root>"
    )
    assert xml == expected


def test_nested_lists():
    data = {"fruits": {"fruit": ["apple", "banana", "cherry"]}}
    xml = to_xml(data, root_name="inventory")
    expected = (
        "<inventory>"
        "<fruits>"
        "<fruit>apple</fruit>"
        "<fruit>banana</fruit>"
        "<fruit>cherry</fruit>"
        "</fruits>"
        "</inventory>"
    )
    assert xml == expected


def test_primitive_root():
    # If obj is not a dict, wrap it in one
    data = "Hello"
    xml = to_xml(data, root_name="message")
    assert xml == "<message><message>Hello</message></message>"


def test_none_value():
    data = {"note": None}
    xml = to_xml(data, root_name="root")
    # None should become empty text
    assert xml == "<root><note></note></root>"


def test_boolean_and_numbers():
    data = {"flag": True, "count": 100, "pi": 3.1415}
    xml = to_xml(data, root_name="root")
    assert (
        xml
        == "<root><flag>True</flag><count>100</count><pi>3.1415</pi></root>"
    )


def test_special_chars():
    data = {"text": "<hello & goodbye>"}
    xml = to_xml(data, root_name="root")
    # Should escape <, >, &
    assert xml == "<root><text>&lt;hello &amp; goodbye&gt;</text></root>"


def test_empty_dict():
    data = {}
    xml = to_xml(data, root_name="empty")
    assert xml == "<empty></empty>"


def test_complex_structure():
    data = {
        "data": {
            "items": [{"id": 1, "value": "alpha"}, {"id": 2, "value": "beta"}],
            "metadata": {"created": "2024-01-01", "author": "Tester"},
        }
    }
    xml = to_xml(data, root_name="root")
    expected = (
        "<root>"
        "<data>"
        "<items>"
        "<id>1</id><value>alpha</value>"
        "</items>"
        "<items>"
        "<id>2</id><value>beta</value>"
        "</items>"
        "<metadata>"
        "<created>2024-01-01</created>"
        "<author>Tester</author>"
        "</metadata>"
        "</data>"
        "</root>"
    )
    assert xml == expected
