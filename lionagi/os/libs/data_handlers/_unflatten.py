import unittest


def unflatten(flat_dict: dict, sep: str = "/") -> dict:
    """
    Unflatten a single-level dictionary into a nested dictionary or list.

    Args:
        flat_dict (dict): The flattened dictionary to unflatten.
        sep (str): The separator used for joining keys. Default: '/'.

    Returns:
        Union[dict, list]: The unflattened nested dictionary or list.
    """

    def _unflatten(data: dict) -> dict | list:
        result = {}
        for key, value in data.items():
            parts = key.split(sep)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if isinstance(value, dict):
                current[parts[-1]] = _unflatten(value)
            else:
                current[parts[-1]] = value

        # Convert dictionary to list if keys are consecutive integers
        if all(isinstance(key, str) and key.isdigit() for key in result):
            return [result[str(i)] for i in range(len(result))] or {}
        return result

    unflattened_dict = {}
    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = unflattened_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    return _unflatten(unflattened_dict)


class TestUnflattenFunction(unittest.TestCase):

    def test_simple_case(self):
        flat_dict = {"a/b": 1, "a/c": 2}
        expected = {"a": {"b": 1, "c": 2}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_multiple_levels(self):
        flat_dict = {"a/b/c": 1, "a/b/d": 2}
        expected = {"a": {"b": {"c": 1, "d": 2}}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_with_different_separator(self):
        flat_dict = {"a.b": 1, "a.c": 2}
        expected = {"a": {"b": 1, "c": 2}}
        self.assertEqual(unflatten(flat_dict, sep="."), expected)

    def test_list_conversion(self):
        flat_dict = {"0/a": 1, "0/b": 2, "1/a": 3, "1/b": 4}
        expected = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        self.assertEqual(unflatten(flat_dict), expected)

    def test_nested_lists(self):
        flat_dict = {"0/0": 1, "0/1": 2, "1/0": 3, "1/1": 4}
        expected = [[1, 2], [3, 4]]
        self.assertEqual(unflatten(flat_dict), expected)

    def test_single_key(self):
        flat_dict = {"a": 1}
        expected = {"a": 1}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_empty_dict(self):
        flat_dict = {}
        expected = {}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_complex_case(self):
        flat_dict = {"a/b/c": 1, "a/b/d": 2, "a/e": 3, "f": 4}
        expected = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_with_dict_value(self):
        flat_dict = {"a/b": {"c/d": 1}}
        expected = {"a": {"b": {"c": {"d": 1}}}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_mixed_types(self):
        flat_dict = {"a/b": 1, "a/c": "string", "a/d": [1, 2, 3]}
        expected = {"a": {"b": 1, "c": "string", "d": [1, 2, 3]}}
        self.assertEqual(unflatten(flat_dict), expected)


if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
