import uuid
from datetime import datetime

import pytest

from lionagi.errors import ItemNotFoundError
from lionagi.protocols.progression import Element, IDType, Progression


@pytest.fixture
def progression_cls():
    return Progression


@pytest.fixture
def simple_id():
    return IDType(uuid.uuid4())


@pytest.fixture
def another_id():
    return IDType(uuid.uuid4())


def test_progression_creation_defaults(progression_cls):
    p = progression_cls()
    assert p.name is None
    assert isinstance(p.order, list)
    assert len(p.order) == 0


def test_progression_create_classmethod(progression_cls, simple_id):
    p = progression_cls.create([simple_id])
    assert len(p) == 1
    assert p.order[0] == simple_id


def test_progression_bool(progression_cls, simple_id):
    p = progression_cls()
    assert not p
    p = progression_cls(order=[simple_id])
    assert p


def test_progression_contains(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id])
    assert simple_id in p
    assert another_id not in p


def test_progression_contains_multiple(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id])
    assert [simple_id, another_id] in p
    # Non-uniform set, or partially missing
    assert [simple_id, IDType(uuid.uuid4())] not in p


def test_progression_get_set_del_item(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id])
    assert p[0] == simple_id
    p[0] = another_id
    assert p[0] == another_id

    del p[0]
    assert len(p) == 1
    assert p[0] == another_id

    # Slice operations
    p = progression_cls(order=[simple_id, another_id, IDType(uuid.uuid4())])
    assert p[1:] == [another_id, p.order[2]]
    p[1:] = [simple_id, simple_id]
    assert p.order == [simple_id, simple_id, simple_id]

    del p[1:]
    assert p.order == [simple_id]


def test_progression_iter(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id])
    items = list(iter(p))
    assert items == [simple_id, another_id]


def test_progression_include(progression_cls, simple_id):
    p = progression_cls()
    assert p.include(simple_id)
    assert simple_id in p.order
    # Including again does nothing (already included)
    assert not p.include(simple_id)


def test_progression_include_multiple(progression_cls, simple_id, another_id):
    p = progression_cls()
    assert p.include([simple_id, another_id])
    assert simple_id in p and another_id in p
    # Including overlapping sets
    assert p.include([another_id, IDType(uuid.uuid4())])


def test_progression_exclude(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id, simple_id])
    # Remove simple_id
    removed = p.exclude(simple_id)
    assert removed is True
    assert simple_id not in p
    # Removing something not present returns False
    assert not p.exclude(simple_id)


def test_progression_append(progression_cls, simple_id, another_id):
    p = progression_cls()
    p.append(simple_id)
    assert p.order == [simple_id]

    # Append multiple
    p.append([another_id, another_id])
    assert p.order == [simple_id, another_id, another_id]


def test_progression_append_element(progression_cls, simple_id):
    class MyElement(Element):
        pass

    e = MyElement(id=simple_id, created_at=datetime.now())
    p = progression_cls()
    p.append(e)
    assert p.order == [simple_id]


def test_progression_pop_popleft(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id])
    popped = p.pop()
    assert popped == another_id
    assert p.order == [simple_id]

    p = progression_cls(order=[simple_id, another_id])
    popped_left = p.popleft()
    assert popped_left == simple_id
    assert p.order == [another_id]


def test_progression_reverse(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id])
    rev = p.__reverse__()
    assert rev.order == [another_id, simple_id]
    assert rev.name == p.name


def test_progression_eq(progression_cls, simple_id, another_id):
    p1 = progression_cls(order=[simple_id])
    p2 = progression_cls(order=[simple_id])
    p3 = progression_cls(order=[another_id])
    assert p1 == p2
    assert p1 != p3


def test_progression_index(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id, simple_id])
    assert p.index(simple_id) == 0
    assert p.index(another_id) == 1
    with pytest.raises(ValueError):
        p.index(IDType(uuid.uuid4()))


def test_progression_remove(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id, simple_id])
    p.remove(simple_id)
    # simple_id should be removed entirely as validate_order returns uniform UUID4 list
    assert simple_id not in p
    # Removing non-existent item raises error
    with pytest.raises(ItemNotFoundError):
        p.remove(IDType(uuid.uuid4()))


def test_progression_count(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, another_id, simple_id])
    assert p.count(simple_id) == 2
    assert p.count(another_id) == 1


def test_progression_extend(progression_cls, simple_id, another_id):
    p1 = progression_cls(order=[simple_id])
    p2 = progression_cls(order=[another_id])
    p1.extend(p2)
    assert p1.order == [simple_id, another_id]

    # Extending with non-Progression raises ValueError
    with pytest.raises(ValueError):
        p1.extend([another_id])


def test_progression_add_operators(progression_cls, simple_id, another_id):
    p1 = progression_cls(order=[simple_id])
    p2 = p1 + another_id
    assert p2.order == [simple_id, another_id]

    p3 = another_id + p1
    assert p3.order == [another_id, simple_id]

    p1 += another_id
    assert p1.order == [simple_id, another_id]


def test_progression_sub_operators(progression_cls, simple_id, another_id):
    p1 = progression_cls(order=[simple_id, another_id, simple_id])
    p2 = p1 - simple_id
    assert p2.order == [another_id]

    p1 -= another_id
    assert p1.order == [simple_id, simple_id]


def test_progression_comparison(progression_cls):
    id1, id2 = IDType(uuid.uuid4()), IDType(uuid.uuid4())
    p1 = progression_cls(order=[id1])
    p2 = progression_cls(order=[id1, id2])
    assert p1 < p2
    assert p2 > p1
    assert p1 <= p2
    assert p2 >= p1


def test_progression_insert(progression_cls, simple_id, another_id):
    p = progression_cls(order=[simple_id, simple_id])
    p.insert(1, another_id)
    assert p.order == [simple_id, another_id, simple_id]

    # Insert multiple items
    new_ids = [IDType(uuid.uuid4()), IDType(uuid.uuid4())]
    p.insert(2, new_ids)
    assert p.order == [
        simple_id,
        another_id,
        new_ids[0],
        new_ids[1],
        simple_id,
    ]
