import unittest
import asyncio
import os
from tempfile import NamedTemporaryFile
from lionagi.utils.sys_util import (
    to_flat_dict,
    to_list,
    str_to_num,
    make_copy,
    to_temp,
    to_csv,
    append_to_jsonl,
    hold_call,
    ahold_call,
    l_call,
    al_call,
    m_call,
    am_call,
    e_call,
    ae_call,
    get_timestamp,
    create_id,
    create_path,
)


class Test_sys_util(unittest.TestCase):
    def test_to_flat_dict(self):
        example_nested_dict = {'a': 1, 'b': {'c': 2}}
        result = to_flat_dict(example_nested_dict)
        self.assertEqual(result, {'a': 1, 'b_c': 2})

    def test_to_list(self):
        example_dict = {'a': 1, 'b': [2, 3]}
        result = to_list(example_dict, flatten_dict=True)
        self.assertEqual(result, [{'a': 1}, {'b_0': 2}, {'b_1': 3}])

    def test_str_to_num(self):
        result = str_to_num("Temperature is -5.6 degrees", num_type=float, precision=1)
        self.assertEqual(result, -5.6)

    def test_make_copy(self):
        sample_dict = {'key': 'value'}
        result = make_copy(sample_dict, 2)
        self.assertEqual(result, [{'key': 'value'}, {'key': 'value'}])

    # def test_to_temp(self):
    #     temp_file = to_temp({'a': 1, 'b': [2, 3]}, flatten_dict=True)
    #     self.assertTrue(isinstance(temp_file, NamedTemporaryFile))

    def test_to_csv(self):
        data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        filepath = 'test_people.csv'
        to_csv(data, filepath, file_exist_ok=True)
        self.assertTrue(os.path.exists(filepath))

    # def test_append_to_jsonl(self):
    #     data = {"key": "value"}
    #     filepath = 'test_data.jsonl'
    #     append_to_jsonl(data, filepath)
    #     with open(filepath, 'r') as f:
    #         lines = f.readlines()
    #         self.assertTrue(len(lines) == 1)
    #         self.assertEqual(lines[0].strip(), '{"key": "value"}')

    def test_hold_call(self):
        def add_one(x):
            return x + 1

        result = hold_call(5, add_one, sleep=2)
        self.assertEqual(result, 6)

    def test_ahold_call(self):
        async def async_add_one(x):
            return x + 1

        result = asyncio.run(ahold_call(5, async_add_one, sleep=2))
        self.assertEqual(result, 6)

    def test_l_call(self):
        def square(x):
            return x * x

        result = l_call([1, 2, 3], square)
        self.assertEqual(result, [1, 4, 9])

    def test_al_call(self):
        async def async_square(x):
            return x * x

        result = asyncio.run(al_call([1, 2, 3], async_square))
        self.assertEqual(result, [1, 4, 9])

    def test_m_call(self):
        def add_one(x):
            return x + 1

        result = m_call([1, 2], [add_one, add_one])
        self.assertEqual(result, [2, 3])

    def test_am_call(self):
        async def async_add_one(x):
            return x + 1

        result = asyncio.run(am_call([1, 2], [async_add_one, async_add_one]))
        self.assertEqual(result, [2, 3])

    def test_e_call(self):
        def square(x):
            return x**2

        result = e_call([1, 2, 3], [square])
        self.assertEqual(result, [[1], [4], [9]])

    def test_ae_call(self):
        async def async_square(x):
            return x**2

        result = asyncio.run(ae_call([1, 2, 3], [async_square]))
        self.assertEqual(result, [[1], [4], [9]])

    def test_get_timestamp(self):
        result = get_timestamp()
        self.assertTrue(isinstance(result, str))

    def test_create_id(self):
        result = create_id()
        self.assertTrue(isinstance(result, str))
        self.assertEqual(len(result), 16)

    def test_create_path(self):
        result = create_path('/tmp/', 'log.txt', timestamp=False)
        self.assertEqual(result, '/tmp/log.txt')


if __name__ == '__main__':
    unittest.main()
