"""Tests for protocol Progression collection system."""

import random
import string
from typing import Any

import pytest

from lionagi.protocols.progression import Progression
from lionagi.protocols.types import BaseAutoModel, Observable
from lionagi.utils import ItemNotFoundError


class MockItem(BaseAutoModel, Observable):
    """Mock item for testing."""

    value: Any


@pytest.fixture
def sample_items():
    """Fixture providing sample items."""
    return [MockItem(value=i) for i in range(5)]


@pytest.fixture
def sample_progression(sample_items):
    """Fixture providing a sample progression."""
    return Progression(order=[item.id for item in sample_items])


def generate_random_string(length: int) -> str:
    """Generate a random string of specified length."""
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


@pytest.mark.parametrize(
    "input_data",
    [
        [],
        [MockItem(value=i) for i in range(3)],
    ],
)
def test_initialization(input_data):
    """Test progression initialization."""
    prog = Progression(order=input_data)
    assert len(prog) == len(input_data)
    for item in input_data:
        assert item.id in prog.order


def test_initialization_with_name():
    """Test progression initialization with name."""
    name = "test_progression"
    prog = Progression(name=name)
    assert prog.name == name


def test_contains(sample_progression, sample_items):
    """Test contains operation."""
    for item in sample_items:
        assert item in sample_progression
        assert item.id in sample_progression


def test_not_contains(sample_progression):
    """Test not contains operation."""
    assert "non_existent_id" not in sample_progression
    assert MockItem(value="new") not in sample_progression


def test_list_conversion(sample_progression, sample_items):
    """Test list conversion."""
    prog_list = sample_progression.__list__()
    assert isinstance(prog_list, list)
    assert len(prog_list) == len(sample_items)
    assert all(isinstance(item, str) for item in prog_list)


def test_len(sample_progression, sample_items):
    """Test length operation."""
    assert len(sample_progression) == len(sample_items)


@pytest.mark.parametrize(
    "index, expected_type",
    [
        (0, str),
        (slice(0, 2), Progression),
    ],
)
def test_getitem(sample_progression, index, expected_type):
    """Test getitem operation."""
    result = sample_progression[index]
    assert isinstance(result, expected_type)


def test_getitem_out_of_range(sample_progression):
    """Test getitem with out of range index."""
    with pytest.raises(ItemNotFoundError):
        _ = sample_progression[len(sample_progression)]


def test_setitem(sample_progression):
    """Test setitem operation."""
    new_item = MockItem(value="new")
    sample_progression[0] = new_item
    assert sample_progression[0] == new_item.id


def test_setitem_slice(sample_progression):
    """Test setitem with slice."""
    new_items = [MockItem(value=f"new_{i}") for i in range(2)]
    sample_progression[0:2] = new_items
    assert sample_progression[0] == new_items[0].id
    assert sample_progression[1] == new_items[1].id


def test_delitem(sample_progression):
    """Test delitem operation."""
    original_length = len(sample_progression)
    del sample_progression[0]
    assert len(sample_progression) == original_length - 1


def test_delitem_slice(sample_progression):
    """Test delitem with slice."""
    original_length = len(sample_progression)
    del sample_progression[0:2]
    assert len(sample_progression) == original_length - 2


def test_iter(sample_progression, sample_items):
    """Test iteration."""
    for prog_item, item in zip(sample_progression, sample_items):
        assert prog_item == item.id


def test_next(sample_progression, sample_items):
    """Test next operation."""
    assert next(sample_progression) == sample_items[0].id


def test_next_empty():
    """Test next on empty progression."""
    empty_prog = Progression()
    with pytest.raises(StopIteration):
        next(empty_prog)


def test_size(sample_progression, sample_items):
    """Test size operation."""
    assert sample_progression.size() == len(sample_items)


def test_clear(sample_progression):
    """Test clear operation."""
    sample_progression.clear()
    assert len(sample_progression) == 0


@pytest.mark.parametrize(
    "input_item",
    [
        MockItem(value="new"),
        [MockItem(value="new1"), MockItem(value="new2")],
    ],
)
def test_append(sample_progression, input_item):
    """Test append operation."""
    original_length = len(sample_progression)
    sample_progression.append(input_item)
    assert len(sample_progression) > original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert item.id in sample_progression
    else:
        assert input_item.id in sample_progression


def test_pop(sample_progression):
    """Test pop operation."""
    original_length = len(sample_progression)
    popped_item = sample_progression.pop()
    assert len(sample_progression) == original_length - 1
    assert popped_item not in sample_progression


def test_pop_with_index(sample_progression):
    """Test pop with index."""
    original_first_item = sample_progression[0]
    popped_item = sample_progression.pop(0)
    assert popped_item == original_first_item
    assert popped_item not in sample_progression


def test_pop_empty():
    """Test pop on empty progression."""
    empty_prog = Progression()
    with pytest.raises(ItemNotFoundError):
        empty_prog.pop()


@pytest.mark.parametrize(
    "input_item",
    [
        MockItem(value="new"),
        [MockItem(value="new1"), MockItem(value="new2")],
    ],
)
def test_include(sample_progression, input_item):
    """Test include operation."""
    original_length = len(sample_progression)
    sample_progression.include(input_item)
    assert len(sample_progression) > original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert item.id in sample_progression
    else:
        assert input_item.id in sample_progression


@pytest.mark.parametrize(
    "input_item",
    [
        MockItem(value="new"),
        [MockItem(value="new1"), MockItem(value="new2")],
    ],
)
def test_exclude(sample_progression, input_item):
    """Test exclude operation."""
    sample_progression.include(input_item)
    original_length = len(sample_progression)
    sample_progression.exclude(input_item)
    assert len(sample_progression) < original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert item.id not in sample_progression
    else:
        assert input_item.id not in sample_progression


def test_is_empty(sample_progression):
    """Test is_empty operation."""
    assert not sample_progression.is_empty()
    sample_progression.clear()
    assert sample_progression.is_empty()


def test_remove(sample_progression, sample_items):
    """Test remove operation."""
    to_remove = sample_items[2]
    sample_progression.remove(to_remove)
    assert to_remove not in sample_progression


def test_remove_non_existent(sample_progression):
    """Test remove with non-existent item."""
    with pytest.raises(ItemNotFoundError):
        sample_progression.remove("non_existent_id")


def test_popleft(sample_progression, sample_items):
    """Test popleft operation."""
    first_item = sample_items[0]
    popped = sample_progression.popleft()
    assert popped == first_item.id
    assert first_item not in sample_progression


def test_popleft_empty():
    """Test popleft on empty progression."""
    empty_prog = Progression()
    with pytest.raises(ItemNotFoundError):
        empty_prog.popleft()


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_large_progression(size):
    """Test progression with large number of items."""
    large_prog = Progression(order=[MockItem(value=i) for i in range(size)])
    assert len(large_prog) == size
    assert large_prog.size() == size


def test_progression_index_with_item():
    """Test index operation with item."""
    items = [MockItem(value=i) for i in range(5)]
    p = Progression(order=items)
    assert p.index(items[2]) == 2


def test_progression_count_with_item():
    """Test count operation with item."""
    item1 = MockItem(value=1)
    item2 = MockItem(value=2)
    items = [item1, item1, item1, item2, item2]
    p = Progression(order=items)
    assert p.count(items[1]) == 3


@pytest.mark.parametrize("method", ["append", "include"])
def test_progression_append_include_equivalence(method):
    """Test equivalence of append and include operations."""
    p1 = Progression()
    p2 = Progression()

    for i in range(5):
        item = MockItem(value=i)
        getattr(p1, method)(item)
        getattr(p2, method)(item)

    assert p1 == p2


def test_progression_remove_with_item():
    """Test remove operation with item."""
    items = [MockItem(value=i) for i in range(5)]
    p = Progression(order=items)
    p.remove(items[2])
    assert len(p) == 4
    assert items[2].id not in p


def test_progression_serialization():
    """Test progression serialization."""
    prog = Progression(name="test_prog")
    serialized = prog.to_dict()
    deserialized = Progression.from_dict(serialized)
    assert deserialized == prog
    assert deserialized.name == prog.name
