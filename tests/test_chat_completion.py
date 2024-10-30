import pytest


@pytest.fixture
def setup():
    print("setup")
    yield
    print("teardown")


def test1():
    setup
    print("test1")
    setup
    print("test2")
