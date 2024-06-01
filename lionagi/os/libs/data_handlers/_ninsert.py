from ..type_conversion import to_list


def ninsert(
    nested_structure: dict | list,
    /,
    indices: list[str | int],
    value,
    *,
    sep: str = "[^_^]",
    max_depth: int | None = None,
    current_depth: int = 0,
) -> None:
    """
    Insert a value into a nested structure at a specified path, creating
    intermediate dictionaries or lists as needed.

    Args:
        nested_structure (dict | list): The nested structure to modify.
        indices (list[str | int]): The path of keys or indices where the
            value should be inserted.
        value (Any): The value to insert.
        sep (str, optional): Separator for joining parts of the path if
            max_depth is reached. Defaults to "[^_^]".
        max_depth (int | None, optional): Maximum depth to traverse before
            joining remaining parts. Defaults to None.
        current_depth (int, optional): The current depth of recursion.
            Defaults to 0.

    Returns:
        None
    """
    indices = to_list(indices)
    parts_len = len(indices)
    parts_depth = 0

    for i, part in enumerate(indices[:-1]):
        if max_depth is not None and current_depth >= max_depth:
            break

        if isinstance(part, int):
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = indices[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
        elif part not in nested_structure:
            next_part = indices[i + 1]
            nested_structure[part] = [] if isinstance(next_part, int) else {}
        nested_structure = nested_structure[part]
        current_depth += 1
        parts_depth += 1

    if parts_depth < parts_len - 1:
        last_part = sep.join([str(part) for part in indices[parts_depth:]])
    else:
        last_part = indices[-1]

    if isinstance(last_part, int):
        handle_list_insert(nested_structure, last_part, value)
    elif isinstance(nested_structure, list):
        nested_structure.append({last_part: value})
    else:
        nested_structure[last_part] = value


def handle_list_insert(nested_structure: list, part: int, value) -> None:
    """
    Ensure a specified index in a list is occupied by a given value,
    extending the list if necessary.

    This method modifies a list by inserting or replacing an element at a
    specified index. If the index is beyond the current list size, the list
    is extended with `None` values up to the index, then the specified value
    is inserted.

    Args:
        nested_structure (list): The list to modify.
        part (int): The target index for inserting or replacing the value.
        value (Any): The value to be inserted or to replace an existing
            value in the list.

    Note:
        This function directly modifies the input list in place.
    """
    while len(nested_structure) <= part:
        nested_structure.append(None)
    nested_structure[part] = value
