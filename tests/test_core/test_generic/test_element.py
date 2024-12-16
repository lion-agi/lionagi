"""Tests for the Element class."""

from datetime import datetime, timezone

import pytest

from lionagi.core.generic.types import Element
from lionagi.core.typing import IDError
from lionagi.settings import Settings


def test_element_creation():
    """Test basic Element creation."""
    element = Element()
    assert element.ln_id is not None
    assert isinstance(element.timestamp, float)
    assert element.created_datetime is not None
    assert isinstance(element.created_datetime, datetime)


def test_element_with_invalid_id():
    """Test Element creation with invalid ID."""
    with pytest.raises(IDError):
        Element(ln_id="invalid id with spaces")


def test_element_with_timestamp():
    """Test Element creation with timestamp."""
    timestamp = 1234567890.0
    element = Element(timestamp=timestamp)
    assert element.timestamp == timestamp

    # Compare with timezone-aware datetime
    expected_dt = datetime.fromtimestamp(
        timestamp, tz=Settings.Config.TIMEZONE
    )
    assert element.created_datetime == expected_dt


def test_element_with_datetime():
    """Test Element creation with datetime."""
    dt = datetime.now(tz=Settings.Config.TIMEZONE)
    element = Element(timestamp=dt)
    assert element.timestamp == dt.timestamp()
    assert abs(element.created_datetime.timestamp() - dt.timestamp()) < 0.001


def test_element_to_dict():
    """Test Element conversion to dictionary."""
    element = Element()
    dict_repr = element.to_dict()
    assert isinstance(dict_repr, dict)
    assert "ln_id" in dict_repr
    assert "timestamp" in dict_repr
    assert "lion_class" in dict_repr
    assert dict_repr["lion_class"] == "Element"


def test_element_from_dict():
    """Test Element creation from dictionary."""
    original = Element()
    dict_repr = original.to_dict()
    recreated = Element.from_dict(dict_repr)
    assert recreated.ln_id == original.ln_id
    assert recreated.timestamp == original.timestamp


def test_element_str_representation():
    """Test Element string representation."""
    element = Element()
    str_repr = str(element)
    assert "Element" in str_repr
    assert element.ln_id[:6] in str_repr


def test_element_bool():
    """Test Element boolean evaluation."""
    element = Element()
    assert bool(element) is True  # Elements are always True


def test_element_len():
    """Test Element length."""
    element = Element()
    assert len(element) == 1  # Elements always have length 1


def test_element_hash():
    """Test Element hash."""
    element = Element()
    assert hash(element) == hash(element.ln_id)

    # Test hash equality for elements with same ID
    element2 = Element(ln_id=element.ln_id)
    assert hash(element) == hash(element2)


def test_element_equality():
    """Test Element equality."""
    element1 = Element()
    element2 = Element(ln_id=element1.ln_id)
    element3 = Element()

    assert element1.ln_id == element2.ln_id
    assert element1.ln_id != element3.ln_id


def test_element_class_name():
    """Test Element class name."""
    element = Element()
    assert element.class_name() == "Element"
    assert Element.class_name() == "Element"


def test_invalid_timestamp_formats():
    """Test Element creation with invalid timestamp formats."""
    with pytest.raises(ValueError):
        Element(timestamp="not a timestamp")

    with pytest.raises(ValueError):
        Element(timestamp="2023-13-45")  # Invalid date

    with pytest.raises(ValueError):
        Element(timestamp={})  # Invalid type


def test_element_with_timezone():
    """Test Element creation with different timezone inputs."""
    # Test with UTC timestamp
    utc_dt = datetime.now(timezone.utc)
    element = Element(timestamp=utc_dt)
    assert element.created_datetime.tzinfo == Settings.Config.TIMEZONE

    # Test with local timestamp
    local_dt = datetime.now()
    element = Element(timestamp=local_dt)
    assert element.created_datetime.tzinfo == Settings.Config.TIMEZONE

    # Test with specific timezone
    import zoneinfo

    est_tz = zoneinfo.ZoneInfo("America/New_York")
    est_dt = datetime.now(est_tz)
    element = Element(timestamp=est_dt)
    assert element.created_datetime.tzinfo == Settings.Config.TIMEZONE
