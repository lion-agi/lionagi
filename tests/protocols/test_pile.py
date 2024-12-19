# test_pile.py
import asyncio
import pickle

import pytest

from lionagi.protocols.element import ID, Element
from lionagi.protocols.pile import ItemExistsError, ItemNotFoundError, Pile
from lionagi.protocols.progression import Progression
from lionagi.utils import Undefined


class SimpleElement(Element):
    pass


@pytest.fixture
def simple_element_class():
    return SimpleElement


@pytest.fixture
def sample_elements(simple_element_class):
    # Create a few elements
    e1 = simple_element_class()
    e2 = simple_element_class()
    e3 = simple_element_class()
    return e1, e2, e3


@pytest.mark.asyncio
async def test_initialization(sample_elements, simple_element_class):
    e1, e2, _ = sample_elements
    p = Pile(
        item_type=simple_element_class, strict_type=False, collections=[e1, e2]
    )
    assert len(p.collections) == 2
    assert all(isinstance(i, simple_element_class) for i in p.values())

    # Without specifying item_type
    # We no longer allow dict initialization, so let's remove that portion or test actual Elements only.
    # The user requested no dict. If we must test it:
    # We'll remove that test line since we no longer support dict input for `collections`.

    # strict_type=True and passing a subclass
    class SubElement(simple_element_class):
        pass

    se = SubElement()
    with pytest.raises(ValueError):
        Pile(
            item_type=simple_element_class,
            strict_type=True,
            collections=[e1, se],
        )


@pytest.mark.asyncio
async def test_set_and_get(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile()
    # Setting at index 0 on empty pile should insert
    p.set(0, e1)
    p.set(1, e2)
    assert p[0] == e1
    assert p[1] == e2

    # Replace using slice
    p.set(slice(1, 2), e3)
    assert p[1] == e3
    assert len(p) == 2

    # Async set
    await p.aset(2, e2)
    assert p[2] == e2

    # get with default
    assert p.get(999, default="not found") == "not found"
    assert await p.aget(999, default="not found async") == "not found async"
    # get existing
    assert p.get(0) == e1


@pytest.mark.asyncio
async def test_insert(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1])
    p.insert(1, e2)
    assert p[0] == e1
    assert p[1] == e2

    # Insert at start
    p.insert(0, e3)
    assert p[0] == e3
    assert p[1] == e1
    assert p[2] == e2

    # Insert existing item causes ItemExistsError
    with pytest.raises(ItemExistsError):
        p.insert(1, e1)  # e1 already exists


@pytest.mark.asyncio
async def test_pop_and_exclude(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2, e3])
    val = p.pop(e2.id)
    assert val == e2
    assert len(p) == 2

    # pop multiple
    popped = p.pop([e1.id, e3.id])
    assert popped == [e1, e3]
    assert len(p) == 0

    # pop non existing no default -> raise
    with pytest.raises(ItemNotFoundError):
        p.pop("fake-id")

    # with default
    assert p.pop("fake-id", default="not found") == "not found"

    # exclude
    p.set(0, e1)
    p.set(1, e2)
    p.exclude(e1.id)
    assert len(p) == 1
    assert e2.id in p.collections

    # async exclude
    await p.aexclude(e2.id)
    assert len(p) == 0


@pytest.mark.asyncio
async def test_include(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(item_type=type(e1))
    # single item
    assert p.include(e1)
    assert len(p) == 1
    assert p[0] == e1

    # multiple
    p.include([e2, e3])
    assert len(p) == 3
    assert p[1] == e2
    assert p[2] == e3

    # ainclude
    # same element again should not duplicate
    assert await p.ainclude(e1) is True
    assert len(p) == 3

    # invalid input
    assert not p.include(123)


@pytest.mark.asyncio
async def test_clear_and_aclear(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2, e3])
    assert len(p) == 3
    p.clear()
    assert len(p) == 0

    p.include(e1)
    p.include(e2)
    await p.aclear()
    assert len(p) == 0


@pytest.mark.asyncio
async def test_update_and_aupdate(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2])
    e2_new = type(e2)(id=e2.id, created_at=e2.created_at)
    p.update([e2_new, e3])
    assert len(p) == 3
    assert p[1] == e2_new
    assert p[2] == e3

    # async update
    e1_new = type(e1)(id=e1.id, created_at=e1.created_at)
    await p.aupdate([e1_new])
    assert p[0] == e1_new


@pytest.mark.asyncio
async def test_indexing_and_slicing(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2, e3])
    assert p[0] == e1
    assert p[1] == e2
    assert p[2] == e3
    assert p[0:2] == [e1, e2]
    assert p[e3.id] == e3

    # non existing
    with pytest.raises(ItemNotFoundError):
        p["non-existing-id"]


@pytest.mark.asyncio
async def test_strict_type(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(item_type=type(e1), strict_type=True)
    p.set(0, e1)
    assert p[0] == e1

    class OtherElement(Element):
        pass

    oe = OtherElement()

    with pytest.raises(ValueError):
        p.set(1, oe)


@pytest.mark.asyncio
async def test_contains(sample_elements):
    e1, e2, _ = sample_elements
    p = Pile(collections=[e1, e2])
    assert e1.id in p
    assert e2 in p
    # invalid type should just return False (no raise)
    assert not (b"not-an-id" in p)


@pytest.mark.asyncio
async def test_length_and_iteration(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2, e3])
    assert len(p) == 3
    values = list(p)
    assert len(values) == 3
    assert all(k in p.collections.values() for k in values)

    results = []
    async for item in p.AsyncPileIterator(p):
        results.append(item)
    assert results == [e1, e2, e3]


@pytest.mark.asyncio
async def test_async_context_manager(sample_elements):
    e1, e2, _ = sample_elements
    p = Pile(collections=[e1, e2])
    async with p:
        assert p.get(0) == e1
    # Lock released


@pytest.mark.asyncio
async def test_concurrency(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile()

    async def task():
        await p.aset(0, e1)
        await p.aset(1, e2)
        await asyncio.sleep(0.01)
        await p.aset(2, e3)

    t1 = asyncio.create_task(task())
    t2 = asyncio.create_task(task())
    await asyncio.gather(t1, t2)

    assert p[0] == e1
    assert p[1] == e2
    assert p[2] == e3


@pytest.mark.asyncio
async def test_pickle_unpickle(sample_elements):
    e1, e2, e3 = sample_elements
    p = Pile(collections=[e1, e2, e3])
    data = pickle.dumps(p)
    p2 = pickle.loads(data)
    assert len(p2) == 3
    assert p2[0] == e1
    assert p2.lock is not None
    assert p2.async_lock is not None


@pytest.mark.asyncio
async def test_default_in_pop(sample_elements):
    e1, e2, _ = sample_elements
    p = Pile(collections=[e1])
    assert p.pop(e2.id, default="def") == "def"


@pytest.mark.asyncio
async def test_non_element_input(sample_elements):
    e1, _, _ = sample_elements
    p = Pile()
    p.include(e1)
    assert len(p) == 1
    assert isinstance(p[0], Element)

    with pytest.raises(ValueError):
        p.append(123)
