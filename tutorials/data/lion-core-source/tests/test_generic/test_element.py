import time
from datetime import datetime, timezone

import pytest
from lionabc.exceptions import LionIDError
from pydantic_core._pydantic_core import ValidationError

from lion_core.generic.element import Element
from lion_core.sys_utils import SysUtil


@pytest.fixture
def custom_id():
    return SysUtil.id()


@pytest.fixture
def custom_timestamp():
    return 1625097600.0  # 2021-07-01 00:00:00 UTC


def test_initialization(custom_id, custom_timestamp):
    # Default initialization
    element = Element()
    assert isinstance(element.ln_id, str)
    assert isinstance(element.timestamp, float)

    # Initialization with custom ln_id
    element = Element(ln_id=custom_id)
    assert element.ln_id == custom_id

    # Initialization with custom timestamp
    element = Element(timestamp=custom_timestamp)
    assert element.timestamp == custom_timestamp

    # Initialization with both custom ln_id and timestamp
    element = Element(ln_id=custom_id, timestamp=custom_timestamp)
    assert element.ln_id == custom_id
    assert element.timestamp == custom_timestamp


def test_created_datetime_property(custom_timestamp):
    element = Element(timestamp=custom_timestamp)
    expected_datetime = datetime.fromtimestamp(
        custom_timestamp, tz=timezone.utc
    )
    assert element.created_datetime == expected_datetime
    assert element.created_datetime.tzinfo == timezone.utc


def test_ln_id_validator(custom_id):
    # Valid ln_id format
    element = Element(ln_id=custom_id)
    assert element.ln_id == custom_id

    # Invalid ln_id formats
    invalid_ids = ["", " ", "invalid id", "123", "abc123"]
    for invalid_id in invalid_ids:
        with pytest.raises(LionIDError):
            Element(ln_id=invalid_id)


def test_timestamp_validator():
    # Valid timestamp formats
    valid_timestamps = [
        1625097600.0,  # float
        1625097600,  # int
        "2021-07-01T00:00:00+00:00",  # ISO format string
    ]
    for valid_timestamp in valid_timestamps:
        element = Element(timestamp=valid_timestamp)
        assert isinstance(element.timestamp, float)

    # Invalid timestamp formats
    invalid_timestamps = [
        "invalid_time",
        "2021-07-01",  # Incomplete datetime string
    ]

    with pytest.raises(ValueError):
        Element(timestamp="invalid_time")


def test_from_dict_to_dict(custom_id, custom_timestamp):
    original_dict = {
        "ln_id": custom_id,
        "timestamp": custom_timestamp,
    }
    element = Element.from_dict(original_dict)
    result_dict = element.to_dict()

    assert result_dict["ln_id"] == original_dict["ln_id"]
    assert result_dict["timestamp"] == original_dict["timestamp"]
    assert result_dict["lion_class"] == "Element"

    # Conversion with missing fields
    minimal_dict = {"ln_id": custom_id}
    minimal_element = Element.from_dict(minimal_dict)
    assert minimal_element.ln_id == minimal_dict["ln_id"]
    assert isinstance(minimal_element.timestamp, float)


def test_string_representations(custom_id, custom_timestamp):
    element = Element(ln_id=custom_id, timestamp=custom_timestamp)

    str_output = str(element)
    assert "Element" in str_output
    assert custom_id[:6] in str_output
    assert "2021-07-01" in str_output

    repr_output = repr(element)
    assert "Element" in repr_output
    assert custom_id in repr_output
    assert "1625097600.0" in repr_output


def test_boolean_and_length():
    element = Element()
    assert bool(element) is True
    assert len(element) == 1


def test_element_immutability(custom_id):
    element = Element()
    original_id = element.ln_id
    original_timestamp = element.timestamp

    with pytest.raises(ValidationError):
        element.ln_id = custom_id

    with pytest.raises(ValidationError):
        element.timestamp = time.time()

    assert element.ln_id == original_id
    assert element.timestamp == original_timestamp


def test_element_subclass_behavior():
    class CustomElement(Element):
        custom_attr: str = "default"

    custom_element = CustomElement(custom_attr="custom")
    assert isinstance(custom_element.ln_id, str)
    assert isinstance(custom_element.timestamp, float)
    assert custom_element.custom_attr == "custom"

    assert len(custom_element) == 1
    assert bool(custom_element) is True


def test_element_with_future_timestamp():
    future_timestamp = time.time() + 10000  # 10000 seconds in the future
    element = Element(timestamp=future_timestamp)
    assert element.timestamp > time.time()
    assert element.created_datetime > datetime.now(timezone.utc)


def test_element_serialization_consistency():
    element1 = Element()
    time.sleep(0.1)  # Ensure a different timestamp
    element2 = Element()

    dict1 = element1.to_dict()
    dict2 = element2.to_dict()

    assert dict1["ln_id"] != dict2["ln_id"]
    assert dict1["timestamp"] != dict2["timestamp"]
    assert dict1.keys() == dict2.keys()
    assert dict1["lion_class"] == dict2["lion_class"]


def test_element_large_batch_creation():
    batch_size = 10000
    elements = [Element() for _ in range(batch_size)]

    assert len(elements) == batch_size
    assert (
        len({e.ln_id for e in elements}) == batch_size
    )  # All IDs should be unique

    timestamps = [e.timestamp for e in elements]
    assert (
        max(timestamps) - min(timestamps) < 1.0
    )  # All timestamps should be within 1 second


def test_element_from_dict_with_extra_fields(custom_id):
    extra_dict = {
        "ln_id": custom_id,
        "timestamp": time.time(),
    }
    element = Element.from_dict(extra_dict)

    assert element.ln_id == extra_dict["ln_id"]
    assert element.timestamp == extra_dict["timestamp"]


def test_element_to_dict_consistency():
    element = Element()
    dict_repr = element.to_dict()

    assert dict_repr["ln_id"] == element.ln_id
    assert dict_repr["timestamp"] == element.timestamp
    assert dict_repr["lion_class"] == element.__class__.__name__

    # Ensure no extra fields are present
    assert set(dict_repr.keys()) == {"ln_id", "timestamp", "lion_class"}


# File: tests/test_generic/test_element.py
