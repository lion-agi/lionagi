from typing import Any, Callable
from ._ninsert import ninsert


def unflatten(
    flat_dict: dict[str, Any],
    /,
    *,
    sep: str = "[^_^]",
    custom_logic: Callable[[str], Any] | None = None,
    max_depth: int | None = None,
) -> dict | list:
    """
    Reconstruct a nested structure from a flat dictionary with composite keys.

    Given a flat dictionary with keys representing paths, this method rebuilds the
    original nested dictionary or list. It supports custom logic for interpreting
    keys and can limit the reconstruction depth.

    Args:
        flat_dict (dict[str, Any]): A flat dictionary with composite keys to
            unflatten.
        sep (str, optional): The separator used in composite keys, indicating
            nested levels. Defaults to "[^_^]".
        custom_logic (Callable[[str], Any] | None, optional): An optional function
            to process each part of the composite keys. Defaults to None.
        max_depth (int | None, optional): The maximum depth for nesting during
            reconstruction. Defaults to None.

    Returns:
        dict | list: The reconstructed nested dictionary or list.

    Examples:
        >>> flat_dict_ = {'a[^_^]b[^_^]c': 1}
        >>> unflatten(flat_dict_)
        {'a': {'b': {'c': 1}}}

        >>> flat_dict_ = {'0[^_^]a': 1, '1[^_^]b': 2}
        >>> unflatten(flat_dict_)
        [{'a': 1}, {'b': 2}]
    """
    unflattened = {}
    for composite_key, value in flat_dict.items():
        parts = composite_key.split(sep)
        if custom_logic:
            parts = [custom_logic(part) for part in parts]
        else:
            parts = [int(part) if part.isdigit() else part for part in parts]

        if not unflattened and all(isinstance(part, int) for part in parts):
            unflattened = []

        ninsert(unflattened, indices=parts, value=value, sep=sep, max_depth=max_depth)

    if isinstance(unflattened, dict) and all(
        isinstance(k, int) for k in unflattened.keys()
    ):
        max_index = max(unflattened.keys(), default=-1)
        return [unflattened.get(i) for i in range(max_index + 1)]
    return unflattened or {}
