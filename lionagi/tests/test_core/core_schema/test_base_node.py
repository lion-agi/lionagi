import unittest
from lionagi.core.schema.base_node import *
import pandas as pd


class TestBaseComponentFromObj(unittest.TestCase):

    def test_from_obj_with_dict(self):
        obj_dict = {"name": "John", "age": 30}
        result = BaseComponent.from_obj(obj_dict)
        self.assertEqual(result.name, "John")
        self.assertEqual(result.age, 30)

    def test_from_obj_with_json_string(self):
        obj_json_str = '{"name": "John", "age": 30'
        result = BaseComponent.from_obj(obj_json_str, fuzzy_parse=True)
        self.assertEqual(result.name, "John")
        self.assertEqual(result.age, 30)

    def test_from_obj_with_list(self):
        obj_list = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = BaseComponent.from_obj(obj_list)
        # Assuming from_obj returns a list of BaseComponent instances for list input
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "John")
        self.assertEqual(result[1].name, "Jane")

    def test_from_obj_with_series(self):
        obj_series = pd.Series({"name": "John", "age": 30})
        result = BaseComponent.from_obj(obj_series)
        self.assertEqual(result.name, "John")
        self.assertEqual(result.age, 30)

    def test_from_obj_with_dataframe(self):
        obj_df = pd.DataFrame(
            [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        )
        result = BaseComponent.from_obj(obj_df)
        # Assuming from_obj returns a list of BaseComponent instances for DataFrame input
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "John")
        self.assertEqual(result[1].name, "Jane")


class TestBaseComponentToObj(unittest.TestCase):

    def setUp(self):
        # Setup your object here if needed
        self.component = BaseComponent.from_obj(
            {
                "name": "john",
                "age": 30,
                "node_id": "87607c414e2977628a5096762aedf46c",
                "timestamp": "2024_03_10T20_31_28_530171+00_00",
            }
        )

    def test_to_dict(self):
        expected_dict = {
            "node_id": "87607c414e2977628a5096762aedf46c",
            "timestamp": "2024_03_10T20_31_28_530171+00_00",
            "meta": {},
            "name": "john",
            "age": 30,
        }
        self.assertEqual(self.component.to_dict(), expected_dict)

    def test_to_json_str(self):
        expected_json = '{"node_id":"87607c414e2977628a5096762aedf46c","timestamp":"2024_03_10T20_31_28_530171+00_00","meta":{},"name":"john","age":30}'
        self.assertEqual(self.component.to_json_str(), expected_json)

    def test_to_pd_series(self):
        expected_series = pd.Series(
            {
                "node_id": "87607c414e2977628a5096762aedf46c",
                "timestamp": "2024_03_10T20_31_28_530171+00_00",
                "meta": {},
                "name": "john",
                "age": 30,
            }
        )
        pd.testing.assert_series_equal(self.component.to_pd_series(), expected_series)

    def test_to_xml(self):
        expected_xml = "<BaseComponent><node_id>87607c414e2977628a5096762aedf46c</node_id><timestamp>2024_03_10T20_31_28_530171+00_00</timestamp><meta /><name>john</name><age>30</age></BaseComponent>"
        self.assertEqual(self.component.to_xml(), expected_xml)


if __name__ == "__main__":
    unittest.main()
