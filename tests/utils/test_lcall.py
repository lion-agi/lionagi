import pytest

from lionagi.utils.lcall import lcall  # Adjust import path as necessary


class CustomError(Exception):
    pass


def test_single_callable():
    # Single callable should work
    def double(x):
        return x * 2

    assert lcall([1, 2, 3], double) == [2, 4, 6]


def test_iterable_with_single_callable():
    def inc(x):
        return x + 1

    # func as iterable with one callable
    assert lcall([1, 2, 3], [inc]) == [2, 3, 4]


def test_non_callable():
    # If func is not callable and not an iterable with a single callable, raise ValueError
    with pytest.raises(ValueError):
        lcall([1, 2, 3], 123)

    # Iterable with no callable or multiple callables
    with pytest.raises(ValueError):
        lcall([1, 2], [int, str])


def test_sanitize_input():
    # If sanitize_input=True, input should be flattened, dropna and optionally unique
    def identity(x):
        return x

    input_ = [1, None, [2, None, 2], 3, None]
    # flatten and dropna
    out = lcall(input_, identity, sanitize_input=True)
    # After sanitize: flatten=[1,2,2,3], dropna removes None => [1,2,2,3]
    assert out == [1, 2, 2, 3]

    # With unique_input=True
    out = lcall(input_, identity, sanitize_input=True, unique_input=True)
    # Unique after flatten, dropna => [1,2,3]
    assert out == [1, 2, 3]


def test_no_sanitize_input():
    def identity(x):
        return x

    input_ = ((1, 2), "string", None, [3, 4])
    # Without sanitize_input, just wrap if not list
    out = lcall(input_, identity)
    # Should mostly leave structure unchanged, except top-level not flattened:
    # input_ was a tuple, ensure it's converted to list: [(1,2), 'string', None, [3,4]]
    assert out == [(1, 2), "string", None, [3, 4]]


def test_flatten_output():
    def identity(x):
        return x

    input_ = [1, [2, 3], [4, [5, 6]], None]
    # flatten=True, dropna=False
    out = lcall(input_, identity, flatten=True)
    # Should flatten after applying func => [1,2,3,4,[5,6],None]
    # But note lcall only calls func then processes output if flatten or dropna or unique_output?
    # According to the given code, flatten affects output at the end.
    assert out == [1, 2, 3, 4, 5, 6, None]


def test_dropna_output():
    def identity(x):
        return x

    input_ = [1, None, 2, None, 3]
    out = lcall(input_, identity, dropna=True)
    # Should remove None from output => [1,2,3]
    assert out == [1, 2, 3]


def test_unique_output_requires_no_error():
    def identity(x):
        return x

    input_ = [1, 1, 2, 2]
    # unique_output without flatten means we do not flatten output,
    # According to doc, flatten or dropna triggers output post-processing.
    # If flatten=False and unique_output=True => we should still be okay
    # The code snippet suggests that flatten and dropna would call `to_list` again
    # Actually, the given code snippet for lcall says:
    # if flatten or dropna:
    #    out = to_list(out, flatten=flatten, dropna=dropna, unique=unique_output)
    # So if we want unique_output, we must trigger post-processing by flatten or dropna:
    with pytest.raises(ValueError):
        # unique_output=True but we didn't set flatten=True => to_list will raise?
        lcall(input_, identity, unique_output=True)

    # With flatten=True and unique_output=True
    out = lcall(input_, identity, flatten=True, unique_output=True)
    assert out == [1, 2]


def test_interrupted_error_partial_result():
    def sometimes_interrupt(x):
        if x == 2:
            raise InterruptedError("Stop here")
        return x * 10

    input_ = [1, 2, 3]
    # On InterruptedError, return what we have so far
    out = lcall(input_, sometimes_interrupt)
    # We processed '1' to '10' before interruption
    # Should return [10], not raise
    assert out == [10]


def test_other_exceptions_reraised():
    def error_func(x):
        if x == "bad":
            raise CustomError("Oops")
        return x

    input_ = ["good", "bad", "ugly"]
    with pytest.raises(CustomError):
        lcall(input_, error_func)


def test_strings_as_atomic():
    def identity(x):
        return x

    # If flatten is True, strings should remain atomic
    input_ = ["abc", ["def", "ghi"]]
    out = lcall(input_, identity, flatten=True)
    assert out == ["abc", "def", "ghi"]


def test_bytes_and_bytearray_atomic():
    def identity(x):
        return x

    input_ = [b"bytes", bytearray(b"abc")]
    out = lcall(input_, identity, flatten=True)
    # Should remain atomic units
    assert out == [b"bytes", bytearray(b"abc")]


def test_args_and_kwargs():
    def add(x, y=0, z=0):
        return x + y + z

    input_ = [1, 2, 3]
    # Pass args and kwargs
    out = lcall(input_, add, 5, z=10)
    # Each element: x + 5 + 10
    assert out == [16, 17, 18]


def test_sanitize_then_postprocess_output():
    def identity(x):
        return x

    input_ = [1, None, [2, 2], "string", None]
    # Sanitize input: flatten, dropna, unique_input
    # After sanitize_input: [1,2,2,"string"] -> with unique_input: [1,2,"string"]
    # func just returns same: [1,2,"string"]
    # Now flatten (already flat), dropna (no None), unique_output (already unique)
    out = lcall(
        input_,
        identity,
        sanitize_input=True,
        unique_input=True,
        flatten=True,
        dropna=True,
        unique_output=True,
    )
    assert out == [1, 2, "string"]


def test_input_already_list():
    def double(x):
        return x * 2

    # If input_ is already a list and sanitize_input=False
    input_ = [1, 2, 3]
    out = lcall(input_, double)
    assert out == [2, 4, 6]


def test_empty_input():
    def identity(x):
        return x

    # empty input should return empty list
    assert lcall([], identity) == []
    # even if sanitize_input is True
    assert lcall([], identity, sanitize_input=True) == []


def test_complex_nested_no_sanitize():
    def identity(x):
        return x

    input_ = [1, [2, [3, None]], "abc", None]
    # no flatten, dropna: leave structure
    out = lcall(input_, identity)
    assert out == [1, [2, [3, None]], "abc", None]


def test_complex_nested_sanitize_input():
    def identity(x):
        return x

    input_ = [1, None, [2, None, [3, None]], "abc", None]
    # sanitize_input=True => flatten=True, dropna=True automatically (from to_list behavior), unique_input optional
    # Actually, from given code: sanitize_input uses to_list(input_, flatten=True, dropna=True, unique=unique_input)
    # So after sanitize: [1,2,3,"abc"]
    out = lcall(input_, identity, sanitize_input=True)
    assert out == [1, 2, 3, "abc"]


def test_after_processing_no_extra_changes_if_not_requested():
    def identity(x):
        return x

    input_ = [1, 2, 3]
    # Without flatten, dropna, unique_output => output should just be function results
    out = lcall(input_, identity)
    assert out == [1, 2, 3]
