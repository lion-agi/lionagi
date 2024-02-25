import unittest
from lionagi.util.sys_util import SysUtil

class TestChangeDictKey(unittest.TestCase):
    def test_change_existing_key(self):
        test_dict = {'old_key': 'value'}
        SysUtil.change_dict_key(test_dict, 'old_key', 'new_key')
        self.assertIn('new_key', test_dict)
        self.assertNotIn('old_key', test_dict)

    def test_change_non_existing_key(self):
        test_dict = {'key': 'value'}
        SysUtil.change_dict_key(test_dict, 'non_existing_key', 'new_key')
        self.assertNotIn('new_key', test_dict)
        self.assertIn('key', test_dict)

    def test_change_key_to_existing_key(self):
        test_dict = {'old_key': 'value1', 'new_key': 'value2'}
        SysUtil.change_dict_key(test_dict, 'old_key', 'new_key')
        self.assertEqual(test_dict['new_key'], 'value1')

class TestGetTimestamp(unittest.TestCase):
    def test_default_separator(self):
        timestamp = SysUtil.get_timestamp()
        self.assertNotIn(':', timestamp)
        self.assertNotIn('.', timestamp)

    def test_custom_separator(self):
        timestamp = SysUtil.get_timestamp(separator='-')
        self.assertNotIn(':', timestamp)
        self.assertNotIn('.', timestamp)
        self.assertIn('-', timestamp)

class TestIsSchema(unittest.TestCase):
    def test_valid_schema(self):
        test_dict = {'key1': 1, 'key2': 'value'}
        schema = {'key1': int, 'key2': str}
        self.assertTrue(SysUtil.is_schema(test_dict, schema))

    def test_invalid_schema(self):
        test_dict = {'key1': 'value', 'key2': 'value'}
        schema = {'key1': int, 'key2': str}
        self.assertFalse(SysUtil.is_schema(test_dict, schema))

    def test_partial_schema(self):
        test_dict = {'key1': 1}
        schema = {'key1': int, 'key2': str}
        self.assertFalse(SysUtil.is_schema(test_dict, schema))

class TestCreateCopy(unittest.TestCase):
    def test_single_copy(self):
        original = {'key': 'value'}
        copy = SysUtil.create_copy(original)
        self.assertEqual(original, copy)
        self.assertNotEqual(id(original), id(copy))

    def test_multiple_copies(self):
        original = {'key': 'value'}
        copies = SysUtil.create_copy(original, num=2)
        self.assertEqual(len(copies), 2)
        self.assertNotEqual(id(copies[0]), id(copies[1]))

    def test_invalid_num(self):
        with self.assertRaises(ValueError):
            SysUtil.create_copy({}, num=0)

class TestCreateId(unittest.TestCase):
    def test_id_length(self):
        id_ = SysUtil.create_id()
        self.assertEqual(len(id_), 32)

    def test_custom_length(self):
        id_ = SysUtil.create_id(n=16)
        self.assertEqual(len(id_), 16)

class TestGetBins(unittest.TestCase):
    def test_bins_with_small_strings(self):
        input_ = ['a', 'b', 'c', 'd']
        bins = SysUtil.get_bins(input_, upper=2)
        self.assertEqual(len(bins), 4)

    def test_bins_with_large_strings(self):
        input_ = ['a'*1000, 'b'*1000, 'c'*1000]
        bins = SysUtil.get_bins(input_)
        self.assertEqual(len(bins), 3)

    def test_bins_with_empty_input(self):
        bins = SysUtil.get_bins([])
        self.assertEqual(len(bins), 0)
        
if __name__ == '__main__':
    unittest.main()
