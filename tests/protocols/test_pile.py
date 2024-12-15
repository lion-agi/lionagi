"""Tests for protocol Pile collection system."""

import asyncio
import copy
import gc
import pickle
import random
import string
import sys
import weakref
from typing import Any

import pytest

from lionagi.protocols.base import Observable
from lionagi.protocols.models import BaseAutoModel
from lionagi.protocols.pile import Pile
from lionagi.protocols.progression import Progression
from lionagi.utils import ItemNotFoundError


class MockElement(BaseAutoModel, Observable):
    """Mock element for testing."""

    value: Any


@pytest.fixture
def sample_elements():
    """Fixture providing sample elements."""
    return [MockElement(value=i) for i in range(5)]


@pytest.fixture
def sample_pile(sample_elements):
    """Fixture providing a sample pile."""
    return Pile(items=sample_elements)


def generate_random_string(length: int) -> str:
    """Generate a random string of specified length."""
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


@pytest.mark.parametrize(
    "input_data",
    [
        [],
        [MockElement(value=i) for i in range(3)],
    ],
)
def test_initialization(input_data):
    """Test pile initialization."""
    p = Pile(items=input_data)
    assert len(p) == len(input_data)
    for item in input_data:
        assert item.id in p


def test_initialization_with_item_type():
    """Test pile initialization with item type."""
    p = Pile(
        items=[MockElement(value=i) for i in range(3)], item_type=MockElement
    )
    assert p.item_type == {MockElement}

    with pytest.raises(TypeError):
        Pile(items=[1, 2, 3], item_type=MockElement)


def test_getitem_invalid():
    """Test invalid getitem operations."""
    p = Pile(items=[MockElement(value=i) for i in range(3)])
    with pytest.raises(ItemNotFoundError):
        p[10]
    with pytest.raises(ItemNotFoundError):
        p["nonexistent_id"]


def test_contains(sample_pile, sample_elements):
    """Test contains operation."""
    assert sample_elements[0] in sample_pile
    assert sample_elements[0].id in sample_pile
    assert MockElement(value="nonexistent") not in sample_pile


def test_keys_values_items(sample_pile, sample_elements):
    """Test keys, values, and items methods."""
    assert list(sample_pile.keys()) == [e.id for e in sample_elements]
    assert list(sample_pile.values()) == sample_elements
    assert list(sample_pile.items()) == [(e.id, e) for e in sample_elements]


def test_get(sample_pile, sample_elements):
    """Test get operation."""
    assert sample_pile.get(0) == sample_elements[0]
    assert sample_pile.get(sample_elements[1].id) == sample_elements[1]
    assert sample_pile.get("nonexistent", "default") == "default"


def test_pop(sample_pile, sample_elements):
    """Test pop operation."""
    popped = sample_pile.pop(1)
    assert popped == sample_elements[1]
    assert popped not in sample_pile
    assert len(sample_pile) == 4

    with pytest.raises(ItemNotFoundError):
        sample_pile.pop("nonexistent")


def test_remove(sample_pile, sample_elements):
    """Test remove operation."""
    sample_pile.remove(sample_elements[2])
    assert sample_elements[2] not in sample_pile
    assert len(sample_pile) == 4

    with pytest.raises(ItemNotFoundError):
        sample_pile.remove(MockElement(value="nonexistent"))


def test_exclude(sample_pile, sample_elements):
    """Test exclude operation."""
    sample_pile.exclude(sample_elements[3])
    assert sample_elements[3] not in sample_pile
    assert len(sample_pile) == 4

    # Excluding non-existent item should not raise an error
    sample_pile.exclude(MockElement(value="nonexistent"))


def test_clear(sample_pile):
    """Test clear operation."""
    sample_pile.clear()
    assert len(sample_pile) == 0


def test_update(sample_pile, sample_elements):
    """Test update operation."""
    new_elements = [MockElement(value="new1"), MockElement(value="new2")]
    sample_pile.update(new_elements)
    assert len(sample_pile) == 7
    assert all(e in sample_pile for e in new_elements)


def test_is_empty(sample_pile):
    """Test is_empty operation."""
    assert not sample_pile.is_empty()
    sample_pile.clear()
    assert sample_pile.is_empty()


def test_size(sample_pile, sample_elements):
    """Test size operation."""
    assert sample_pile.size() == len(sample_elements)


def test_append(sample_pile, sample_elements):
    """Test append operation."""
    new_element = MockElement(value="new")
    sample_pile.append(new_element)
    assert new_element in sample_pile
    assert len(sample_pile) == 6


def test_insert(sample_pile, sample_elements):
    """Test insert operation."""
    new_element = MockElement(value="new")
    sample_pile.insert(2, new_element)
    assert sample_pile[2] == new_element
    assert len(sample_pile) == 6


def test_iter(sample_pile, sample_elements):
    """Test iteration."""
    for item in sample_pile:
        assert item in sample_elements


def test_strict_mode():
    """Test strict mode."""
    strict_pile = Pile(
        items=[MockElement(value=i) for i in range(3)],
        item_type=MockElement,
        strict=True,
    )
    with pytest.raises(TypeError):
        strict_pile.include(Observable())  # Not a MockElement


def test_order_preservation():
    """Test order preservation."""
    elements = [MockElement(value=i) for i in range(10)]
    p = Pile(items=elements)
    assert list(p.values()) == elements

    # Test order after operations
    p.remove(elements[5])
    p.include(MockElement(value="new"))
    assert list(p.values())[:5] == elements[:5]
    assert list(p.values())[5:9] == elements[6:]
    assert list(p.values())[9].value == "new"


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent operations."""
    p = Pile()

    async def add_items():
        for _ in range(1000):
            p.include(MockElement(value=generate_random_string(10)))
            await asyncio.sleep(0.001)

    async def remove_items():
        for _ in range(500):
            if not p.is_empty():
                p.pop(0)
            await asyncio.sleep(0.001)

    await asyncio.gather(add_items(), remove_items())
    assert 450 <= len(p) <= 550  # Allow for some variance due to timing


def test_large_scale_operations():
    """Test large scale operations."""
    large_pile = Pile(items=[MockElement(value=i) for i in range(100000)])
    assert len(large_pile) == 100000

    # Test various operations on the large pile
    assert large_pile[50000].value == 50000
    large_pile.include(MockElement(value=100000))
    assert len(large_pile) == 100001
    large_pile.exclude(large_pile[50000])
    assert len(large_pile) == 100000
    assert large_pile[50000].value == 50001


def test_memory_efficiency():
    """Test memory efficiency."""
    elements = [MockElement(value=i) for i in range(100000)]
    p = Pile(elements)

    # Calculate memory usage
    pile_size = sys.getsizeof(p)
    internal_size = sum(sys.getsizeof(item) for item in p.pile_.values())
    total_size = pile_size + internal_size

    # Check if memory usage is reasonable (less than 100MB for 100,000 elements)
    assert total_size < 100 * 1024 * 1024  # 100MB in bytes


def test_pile_with_custom_progression():
    """Test pile with custom progression."""
    elements = [MockElement(value=i) for i in range(5)]
    custom_prog = Progression(order=[e.id for e in elements])
    p = Pile(elements, order=custom_prog)
    assert p.progress == custom_prog


def test_pile_with_invalid_order():
    """Test pile with invalid order."""
    elements = [MockElement(value=i) for i in range(5)]
    with pytest.raises(ValueError):
        Pile(elements, order=[1, 2, 3])  # Order length doesn't match items


def test_pile_with_complex_elements():
    """Test pile with complex elements."""

    class ComplexElement(BaseAutoModel, Observable):
        data: dict

    elements = [
        ComplexElement(data={"value": i, "nested": {"x": i * 2}})
        for i in range(5)
    ]
    p = Pile(items=elements)
    assert len(p) == 5
    assert all(isinstance(e, ComplexElement) for e in p.values())
    assert p[2].data["nested"]["x"] == 4


def test_pile_with_generator_input():
    """Test pile with generator input."""

    def element_generator():
        for i in range(1000):
            yield MockElement(value=i)

    p = Pile(element_generator())
    assert len(p) == 1000
    assert all(i == e.value for i, e in enumerate(p.values()))


@pytest.mark.asyncio
async def test_pile_with_async_generator_input():
    """Test pile with async generator input."""

    async def async_element_generator():
        for i in range(1000):
            await asyncio.sleep(0.001)
            yield MockElement(value=i)

    p = Pile(items=[e async for e in async_element_generator()])
    assert len(p) == 1000
    assert all(i == e.value for i, e in enumerate(p.values()))


def test_pile_exception_handling():
    """Test pile exception handling."""
    p = Pile(items=[MockElement(value=i) for i in range(5)])

    with pytest.raises(ItemNotFoundError):
        p[1.5]  # Non-integer, non-string index

    with pytest.raises(ItemNotFoundError):
        p.remove(MockElement(value=10))  # Element not in pile

    with pytest.raises(ValueError):
        p.update(5)  # Invalid update input


def test_pile_pickling():
    """Test pile pickling."""
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    pickled = pickle.dumps(p)
    unpickled = pickle.loads(pickled)
    assert p == unpickled


def test_pile_deep_copy():
    """Test pile deep copy."""
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    p_copy = copy.deepcopy(p)
    assert p == p_copy
    assert p is not p_copy
    assert all(a is not b for a, b in zip(p.values(), p_copy.values()))


@pytest.mark.parametrize("n", [10, 100, 1000])
def test_pile_memory_usage(n):
    """Test pile memory usage."""
    p = Pile(items=[MockElement(value=i) for i in range(n)])
    memory_usage = sys.getsizeof(p) + sum(sys.getsizeof(e) for e in p.values())

    # Rough estimation: each MockElement should take about 100 bytes
    expected_usage = sys.getsizeof(p) + n * 100
    assert memory_usage < expected_usage * 1.2  # Allow 20% margin


def test_pile_with_weakref():
    """Test pile with weakref."""
    p = Pile()
    refs = []
    elements = []  # Keep strong references during pile lifetime

    for _ in range(10):
        e = MockElement(value=_)
        elements.append(e)  # Keep strong reference
        weak_e = weakref.ref(e)
        refs.append(weak_e)
        p.include(e)

    del p
    del elements  # Remove strong references
    gc.collect()
    gc.collect()  # Second collection to ensure cleanup

    # Allow for some references to persist due to Python's reference counting
    assert sum(ref() is not None for ref in refs) <= 1


@pytest.fixture
async def async_sample_pile():
    """Fixture providing an async sample pile."""
    return Pile([MockElement(value=i) for i in range(5)])


@pytest.mark.asyncio
async def test_async_setitem(async_sample_pile):
    """Test async setitem operation."""
    await async_sample_pile.asetitem(2, MockElement(value=10))
    assert async_sample_pile[2].value == 10

    with pytest.raises(ItemNotFoundError):
        await async_sample_pile.asetitem(10, MockElement(value=20))


@pytest.mark.asyncio
async def test_async_remove(async_sample_pile):
    """Test async remove operation."""
    element = async_sample_pile[2]
    await async_sample_pile.aremove(element)
    assert len(async_sample_pile) == 4
    assert element not in async_sample_pile

    with pytest.raises(ItemNotFoundError):
        await async_sample_pile.aremove(MockElement(value=100))


@pytest.mark.asyncio
async def test_async_include(async_sample_pile):
    """Test async include operation."""
    new_element = MockElement(value=100)
    await async_sample_pile.ainclude(new_element)
    assert len(async_sample_pile) == 6
    assert new_element in async_sample_pile


@pytest.mark.asyncio
async def test_async_exclude(async_sample_pile):
    """Test async exclude operation."""
    element = async_sample_pile[2]
    await async_sample_pile.aexclude(element)
    assert len(async_sample_pile) == 4
    assert element not in async_sample_pile

    # Excluding non-existent element should not raise an error
    await async_sample_pile.aexclude(MockElement(value=100))


@pytest.mark.asyncio
async def test_async_update(async_sample_pile):
    """Test async update operation."""
    new_elements = [MockElement(value=i) for i in range(5, 8)]
    await async_sample_pile.aupdate(new_elements)
    assert len(async_sample_pile) == 8


@pytest.mark.asyncio
async def test_async_get(async_sample_pile):
    """Test async get operation."""
    element = await async_sample_pile.aget(2)
    assert element.value == 2

    default = object()
    assert await async_sample_pile.aget(10, default) is default


@pytest.mark.asyncio
async def test_async_iter(async_sample_pile):
    """Test async iteration."""
    values = []
    async for item in async_sample_pile:
        values.append(item.value)
    assert values == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_async_next(async_sample_pile):
    """Test async next operation."""
    aiter = async_sample_pile.__aiter__()
    assert (await aiter.__anext__()).value == 0
    assert (await aiter.__anext__()).value == 1

    # Exhaust the iterator
    for _ in range(3):
        await aiter.__anext__()

    with pytest.raises(StopAsyncIteration):
        await aiter.__anext__()


@pytest.mark.asyncio
async def test_async_pile_as_queue():
    """Test async pile as queue."""
    p = Pile()

    async def producer():
        for i in range(100):
            await p.ainclude(MockElement(value=i))
            await asyncio.sleep(0.001)

    async def consumer():
        consumed = []
        while len(consumed) < 100:
            try:
                item = await p.apop(0)
                consumed.append(item)
            except ItemNotFoundError:
                await asyncio.sleep(0.001)
        return consumed

    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    consumed_items = await consumer_task
    await producer_task

    assert len(consumed_items) == 100
    assert [item.value for item in consumed_items] == list(range(100))
    assert len(p) == 0


@pytest.mark.asyncio
async def test_async_error_recovery():
    """Test async error recovery."""
    p = Pile()

    async def faulty_operation():
        await p.ainclude(MockElement(value="valid"))
        raise ValueError("Simulated error")

    try:
        await faulty_operation()
    except ValueError:
        pass

    assert len(p) == 1

    await p.ainclude(MockElement(value="after_error"))
    assert len(p) == 2


@pytest.mark.asyncio
async def test_async_type_checking():
    """Test async type checking."""
    p = Pile(item_type={MockElement})

    await p.ainclude(MockElement(value=1))

    with pytest.raises(TypeError):
        await p.ainclude("not a MockElement")

    assert len(p) == 1
