from enum import Enum
from typing import Any

import pytest
from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

from lionagi.utils import UndefinedType, to_dict


class SampleEnum(Enum):
    A = 1
    B = 2


class SimpleModel(BaseModel):
    x: int
    y: str

    def to_json(self):
        return f'{{"x": {self.x}, "y": "{self.y}"}}'


class ModelWithDump(BaseModel):
    a: int
    b: str

    def model_dump(self):
        return {"A": self.a, "B": self.b}


def custom_parser(s: str) -> Any:
    # A trivial custom parser that returns a fixed dict
    return {"parsed": True, "original": s}


def test_basic_dict():
    data = {"key": "value", "num": 42}
    result = to_dict(data)
    assert result == data


def test_basic_list():
    data = [1, 2, 3]
    result = to_dict(data)
    # list becomes { "0": 1, "1": 2, "2": 3 } since iterable->dict conversion
    assert result == {"0": 1, "1": 2, "2": 3}


def test_basic_set():
    data = {"a", "b"}
    result = to_dict(data)
    # set -> {"a": "a", "b": "b"}
    assert result == {"a": "a", "b": "b"}


def test_enum_use_values():
    result = to_dict(SampleEnum, use_enum_values=True)
    # Expect enum members: { "A": 1, "B": 2 }
    assert result == {"A": 1, "B": 2}


def test_enum_use_names():
    result = to_dict(SampleEnum, use_enum_values=False)
    # Expect { "A": "A", "B": "B" }
    assert result == {"A": "A", "B": "B"}


def test_none_undefined():
    result_none = to_dict(None)
    assert result_none == {}

    result_undef = to_dict(UndefinedType())
    assert result_undef == {}

    result_pundef = to_dict(PydanticUndefinedType)
    assert result_pundef == {}


def test_basic_str_json():
    json_str = '{"name": "John", "age": 30}'
    result = to_dict(json_str, str_type="json")
    assert result == {"name": "John", "age": 30}


def test_fuzzy_json():
    # Missing quotes around key
    json_str = "{name: 'Jane', age:25}"
    result = to_dict(json_str, str_type="json", fuzzy_parse=True)
    assert result == {"name": "Jane", "age": 25}


def test_xml_parse():
    xml_str = "<root><item>value</item></root>"
    result = to_dict(xml_str, str_type="xml")
    # {'root': {'item': 'value'}}
    assert result == {"root": {"item": "value"}}


def test_xml_remove_root():
    xml_str = "<root><item>value</item></root>"
    result = to_dict(xml_str, str_type="xml", remove_root=True)
    # remove_root -> {'item': 'value'}
    assert result == {"item": "value"}


def test_xml_custom_root():
    xml_str = "<data><item>value</item></data>"
    result = to_dict(xml_str, str_type="xml", root_tag="custom_root")
    # wrap under custom_root:
    # old root was "data", now -> {'custom_root': {'item': 'value'}}
    assert result == {"custom_root": {"item": "value"}}


def test_suppress():
    # Invalid JSON but suppress=True
    bad_json = "not really json"
    result = to_dict(bad_json, str_type="json", suppress=True)
    assert result == {}


def test_custom_parser():
    # Use our custom parser
    text = "some text"
    result = to_dict(text, parser=custom_parser)
    assert result == {"parsed": True, "original": "some text"}


def test_recursive_basic():
    nested = {"a": {"b": '{"x":10}'}}  # inner string is JSON
    # recursive=True should parse the inner string after first pass
    result = to_dict(nested, recursive=True)
    # after recursion: {"a": {"b": {"x":10}}}
    assert result == {"a": {"b": {"x": 10}}}


def test_recursive_max_depth():
    # max depth of 1 should not parse inner strings:
    nested = {"a": {"b": '{"c":20}'}}
    result = to_dict(nested, recursive=True, max_recursive_depth=1)
    # Only one recursion allowed:
    # at depth=0: "a" is dict -> ok parse
    # at "b": we are at depth=1, this means we can't parse the inner string
    # So "b" stays '{"c":20}' as a string
    assert result == {"a": {"b": '{"c":20}'}}


def test_recursive_python_only():
    # If recursive_python_only=True,
    # it should not try to parse custom objects that are not python built-ins
    class CustomObj:
        def to_json(self):
            return '{"custom":true}'

    data = {"x": CustomObj()}
    result = to_dict(data, recursive=True, recursive_python_only=True)
    # It won't parse CustomObj because it's not a python builtin and no direct method is used
    # Actually tries _model_to_dict fallback. If it fails, returns object as is.
    # CustomObj has to_json, so it may parse it. Let's remove that method.
    # Let's redefine it here quickly:

    class CustomObjNoJson:
        pass

    data = {"x": CustomObjNoJson()}
    result = to_dict(data, recursive=True, recursive_python_only=True)
    # No custom parsing, returns object as is.
    assert "x" in result
    assert isinstance(result["x"], CustomObjNoJson)


def test_model_with_dump():
    m = ModelWithDump(a=1, b="B")
    # use_model_dump = True
    result = to_dict(m, use_model_dump=True)
    assert result == {"A": 1, "B": "B"}


def test_model_no_dump():
    m = SimpleModel(x=10, y="test")
    # SimpleModel doesn't have model_dump but has to_json
    result = to_dict(m, use_model_dump=False)
    # Will try to_json, result = {"x":10,"y":"test"}
    assert result == {"x": 10, "y": "test"}


def test_iterable_no_sequence():
    # If not a sequence or BaseModel, tries to convert dict or fallback
    # Let's try with a generator
    gen = (i for i in range(3))
    result = to_dict(gen)
    # {"0":0,"1":1,"2":2}
    assert result == {"0": 0, "1": 1, "2": 2}


def test_empty_string_input():
    # empty string with suppress=False should raise
    with pytest.raises(ValueError):
        to_dict("")


def test_str_with_invalid_json_no_suppress():
    bad = "not json"
    with pytest.raises(ValueError):
        to_dict(bad, str_type="json", fuzzy_parse=False)


def test_str_with_invalid_xml_no_suppress():
    bad = "<root><unclosed>"
    with pytest.raises(ValueError):
        to_dict(bad, str_type="xml")


def test_overload_types():
    # Just a static type check scenario, no runtime effect:
    # if recursive=False, returns dict
    result = to_dict({"test": "value"}, recursive=False)
    assert isinstance(result, dict)

    # if recursive=True, may return Any
    result_any = to_dict({"test": "value"}, recursive=True)
    # can't assert type at runtime easily, but we know it's Any (no effect here)


def test_fuzzy_parse_non_json():
    # fuzzy_parse only relevant for JSON
    xml_str = "<root><val>1</val></root>"
    # fuzzy_parse with XML should not matter
    result = to_dict(xml_str, str_type="xml", fuzzy_parse=True)
    assert result == {"root": {"val": "1"}}
