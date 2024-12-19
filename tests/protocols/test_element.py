import uuid
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from lionagi.protocols.element import (
    ID,
    LION_CLASS_REGISTRY,
    Element,
    IDType,
    get_class,
)


@pytest.fixture
def element_cls():
    # Return the Element class fixture for convenience.
    return Element


def test_element_creation_defaults(element_cls):
    """Test creation of an Element with default fields."""
    elem = element_cls()
    assert isinstance(elem.id, IDType), "id must be a UUID instance"
    assert isinstance(
        elem.created_at, datetime
    ), "created_at must be a datetime"
    # Ensure created_at is roughly now (within a few seconds)
    assert (datetime.now() - elem.created_at) < timedelta(
        seconds=5
    ), "created_at should be near current time"


def test_element_creation_custom_fields(element_cls):
    """Test creating an Element with custom id and created_at."""
    custom_id = uuid.uuid4()
    custom_time = datetime(2020, 1, 1, 12, 0, 0)
    elem = element_cls(id=custom_id, created_at=custom_time)
    assert elem.id == IDType(id=custom_id)
    assert elem.created_at == custom_time


def test_element_to_dict(element_cls):
    """Test that to_dict returns a dictionary with the correct fields."""
    elem = element_cls()
    d = elem.to_dict()
    assert "id" in d
    assert "created_at" in d
    assert "lion_class" in d
    assert d["lion_class"] == elem.class_name()


def test_element_from_dict(element_cls):
    """Test from_dict deserialization."""
    elem = element_cls()
    d = elem.to_dict()
    new_elem = element_cls.from_dict(d)
    assert new_elem.id == elem.id
    assert new_elem.created_at == elem.created_at
    assert isinstance(new_elem, element_cls)


def test_element_equality(element_cls):
    """Test __eq__ and hashing of Elements."""
    e1 = element_cls()
    e2 = element_cls()
    e3 = element_cls(id=e1.id, created_at=e1.created_at)

    assert e1 != e2, "Elements with different IDs should not be equal"
    assert e1 == e3, "Elements with the same ID should be equal"
    # Test hash
    s = {e1, e2, e3}
    # There should be only 2 unique elements based on IDs
    assert len(s) == 2


def test_element_str_repr(element_cls):
    """Test __str__ and __repr__ methods for consistency."""
    e = element_cls()
    s = str(e)
    r = repr(e)
    assert s == r, "__str__ and __repr__ should match"
    assert (
        e.class_name() in s
    ), "String representation should include class name"
    assert (
        str(e.id) in s
    ), "String representation should include the element ID"


def test_element_bool(element_cls):
    """Test boolean conversion of an Element (always True)."""
    e = element_cls()
    assert bool(e) is True


def test_element_len(element_cls):
    """Test __len__ method of Element."""
    e = element_cls()
    # By contract, Element __len__ returns 1
    assert len(e) == 1


def test_element_validate_id(element_cls):
    """Ensure that invalid IDs raise ValidationError."""
    with pytest.raises(ValidationError):
        element_cls(id="not-a-valid-uuid")


def test_element_validate_created_at(element_cls):
    """Ensure that invalid created_at values raise ValidationError."""
    with pytest.raises(ValidationError):
        element_cls(created_at="not-a-valid-datetime")


def test_element_serialization(element_cls):
    """Test that serialization from model_dump (pydantic) works as expected."""
    e = element_cls()
    d = e.model_dump()
    # Check fields
    assert "id" in d
    assert "created_at" in d
    # Check that serialization of fields matches what we expect
    assert isinstance(d["id"], str)
    assert isinstance(d["created_at"], str)


def test_element_from_dict_no_lion_class(element_cls):
    """Test from_dict if 'lion_class' is missing."""
    e = element_cls()
    d = e.to_dict()
    d.pop("lion_class")
    # from_dict should still work and return an Element instance
    new_e = element_cls.from_dict(d)
    assert isinstance(new_e, element_cls)
    assert new_e.id == e.id
    assert new_e.created_at == e.created_at
