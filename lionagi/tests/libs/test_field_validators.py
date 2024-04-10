import unittest
from unittest.mock import patch
from lionagi.libs.ln_validate import (
    check_dict_field,
    check_action_field,
    check_number_field,
    check_bool_field,
    check_str_field,
    check_enum_field,
    _fix_action_field,
    _fix_number_field,
    _fix_bool_field,
    _fix_str_field,
    _fix_enum_field,
)


class TestValidationFunctions(unittest.TestCase):
    def test_check_dict_field_valid(self):
        x = {"key": "value"}
        keys = ["key"]
        result = check_dict_field(x, keys)
        self.assertEqual(result, x)

    def test_fix_action_field_invalid_string(self):
        x = '[{"invalid_key": "value"}]'
        try:
            _fix_action_field(x)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field: {'invalid_key': 'value'}")

    def test_fix_action_field_invalid_discard_disabled(self):
        x = '[{"function": "func1", "arguments": {}}, {"invalid_key": "value"}]'
        try:
            _fix_action_field(x, discard_=False)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field: {'invalid_key': 'value'}")

    def test_check_dict_field_invalid_fixable(self):
        x = '{"key": "value"}'
        keys = ["key"]
        result = check_dict_field(x, keys, fix_=True)
        self.assertEqual(result, {"key": "value"})

    def test_check_dict_field_invalid_not_fixable(self):
        x = '{"invalid_key": "value"}'
        keys = ["key"]
        with self.assertRaises(ValueError) as cm:
            check_dict_field(x, keys, fix_=False)
        self.assertEqual(
            str(cm.exception), "Default value for DICT must be a dict, got str"
        )

    def test_check_action_field_invalid_not_fixable(self):
        x = '[{"invalid_key": "value"}]'
        try:
            check_action_field(x, fix_=False)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field type.")

    def test_check_action_field_invalid_fix_disabled(self):
        x = '[{"function": "func1", "arguments": {}}, {"invalid_key": "value"}]'
        try:
            check_action_field(x, fix_=False)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field type.")

    def test_check_action_field_valid(self):
        x = [
            {"function": "func1", "arguments": {}},
            {"function": "func2", "arguments": {}},
        ]
        result = check_action_field(x)
        self.assertEqual(result, x)

    def test_check_action_field_invalid_fixable(self):
        x = '[{"function": "func1", "arguments": {}}, {"function": "func2", "arguments": {}}]'
        result = check_action_field(x, fix_=True)
        self.assertEqual(
            result,
            [
                {"function": "func1", "arguments": {}},
                {"function": "func2", "arguments": {}},
            ],
        )

    def test_check_action_field_invalid_fix_disabled(self):
        x = '[{"function": "func1", "arguments": {}}, {"invalid_key": "value"}]'
        try:
            check_action_field(x, fix_=False)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field type.")

    def test_check_number_field_valid(self):
        x = 42
        result = check_number_field(x)
        self.assertEqual(result, x)

    def test_check_number_field_invalid_fixable(self):
        x = "42"
        result = check_number_field(x, fix_=True)
        self.assertEqual(result, 42)

    def test_check_number_field_invalid_not_fixable(self):
        x = "not_a_number"
        with self.assertRaises(ValueError) as cm:
            check_number_field(x, fix_=True)
        self.assertEqual(
            str(cm.exception), "Failed to convert not_a_number into a numeric value"
        )

    def test_check_number_field_invalid_fix_disabled(self):
        x = "42"
        with self.assertRaises(ValueError) as cm:
            check_number_field(x, fix_=False)
        self.assertEqual(
            str(cm.exception),
            "Default value for NUMERIC must be an int or float, got str",
        )

    def test_check_bool_field_valid(self):
        x = True
        result = check_bool_field(x)
        self.assertEqual(result, x)

    def test_check_bool_field_invalid_fixable(self):
        x = "true"
        result = check_bool_field(x, fix_=True)
        self.assertTrue(result)

    def test_check_bool_field_invalid_not_fixable(self):
        x = "not_a_boolean"
        with self.assertRaises(ValueError) as cm:
            check_bool_field(x, fix_=True)
        self.assertEqual(
            str(cm.exception), "Failed to convert not_a_boolean into a boolean value"
        )

    def test_check_bool_field_invalid_fix_disabled(self):
        x = "true"
        with self.assertRaises(ValueError) as cm:
            check_bool_field(x, fix_=False)
        self.assertEqual(
            str(cm.exception), "Default value for BOOLEAN must be a bool, got str"
        )

    def test_check_str_field_valid(self):
        x = "hello"
        result = check_str_field(x)
        self.assertEqual(result, x)

    def test_check_str_field_invalid_fixable(self):
        x = 42
        result = check_str_field(x, fix_=True)
        self.assertEqual(result, "42")

    def test_check_str_field_invalid_not_fixable(self):
        x = object()
        try:
            check_str_field(x, fix_=False)
        except ValueError as e:
            self.assertEqual(
                str(e), "Default value for STRING must be a str, got object"
            )

    def test_check_str_field_invalid_fix_disabled(self):
        x = 42
        with self.assertRaises(ValueError) as cm:
            check_str_field(x, fix_=False)
        self.assertEqual(
            str(cm.exception), "Default value for STRING must be a str, got int"
        )

    def test_check_enum_field_valid(self):
        x = "option1"
        choices = ["option1", "option2"]
        result = check_enum_field(x, choices)
        self.assertEqual(result, x)

    def test_check_enum_field_invalid_fixable(self):
        x = "option3"
        choices = ["option1", "option2"]
        with patch("lionagi.libs.ln_validate._fix_enum_field", return_value="option1"):
            result = check_enum_field(x, choices, fix_=True)
        self.assertEqual(result, "option1")

    def test_check_enum_field_invalid_not_fixable(self):
        x = "option3"
        choices = ["option1", "option2"]
        with self.assertRaises(ValueError) as cm:
            check_enum_field(x, choices, fix_=False)
        self.assertEqual(
            str(cm.exception),
            "Default value for ENUM must be one of the ['option1', 'option2'], got option3",
        )

    def test_check_enum_field_invalid_choices(self):
        x = "option1"
        choices = ["option1", 42]
        with self.assertRaises(ValueError) as cm:
            check_enum_field(x, choices)
        self.assertEqual(
            str(cm.exception),
            "Field type ENUM requires all choices to be of the same type, got ['option1', 42]",
        )

    def test_check_enum_field_invalid_type(self):
        x = 42
        choices = ["option1", "option2"]
        with self.assertRaises(ValueError) as cm:
            check_enum_field(x, choices)
        self.assertEqual(
            str(cm.exception),
            "Default value for ENUM must be an instance of the str, got int",
        )

    def test_fix_action_field_string(self):
        x = '[{"function": "func1", "arguments": {}}, {"function": "func2", "arguments": {}}]'
        result = _fix_action_field(x)
        self.assertEqual(
            result,
            [
                {"function": "func1", "arguments": {}},
                {"function": "func2", "arguments": {}},
            ],
        )

    def test_fix_action_field_invalid_string(self):
        x = '[{"invalid_key": "value"}]'
        try:
            _fix_action_field(x)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field: {'invalid_key': 'value'}")

    def test_fix_action_field_invalid_discard_disabled(self):
        x = '[{"function": "func1", "arguments": {}}, {"invalid_key": "value"}]'
        try:
            _fix_action_field(x, discard_=False)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid action field: {'invalid_key': 'value'}")

    def test_fix_number_field_valid(self):
        x = "42"
        result = _fix_number_field(x)
        self.assertEqual(result, 42)

    def test_fix_number_field_invalid(self):
        x = "not_a_number"
        with self.assertRaises(ValueError) as cm:
            _fix_number_field(x)
        self.assertEqual(
            str(cm.exception), "Failed to convert not_a_number into a numeric value"
        )

    def test_fix_bool_field_true(self):
        x = "true"
        result = _fix_bool_field(x)
        self.assertTrue(result)

    def test_fix_bool_field_false(self):
        x = "false"
        result = _fix_bool_field(x)
        self.assertFalse(result)

    def test_fix_bool_field_invalid(self):
        x = "not_a_boolean"
        with self.assertRaises(ValueError) as cm:
            _fix_bool_field(x)
        self.assertEqual(
            str(cm.exception), "Failed to convert not_a_boolean into a boolean value"
        )

    def test_fix_str_field_valid(self):
        x = 42
        result = _fix_str_field(x)
        self.assertEqual(result, "42")

    def test_fix_str_field_invalid(self):
        x = object()
        try:
            _fix_str_field(x)
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Failed to convert <object object at 0x{:x}> into a string value".format(
                    id(x)
                ),
            )

    def test_fix_enum_field_valid(self):
        x = "option3"
        choices = ["option1", "option2"]
        with patch(
            "lionagi.libs.StringMatch.choose_most_similar", return_value="option1"
        ):
            result = _fix_enum_field(x, choices)
        self.assertEqual(result, "option1")

    def test_fix_enum_field_invalid(self):
        x = "option3"
        choices = ["option1", "option2"]
        with patch(
            "lionagi.libs.StringMatch.choose_most_similar",
            side_effect=ValueError("No match found"),
        ):
            with self.assertRaises(ValueError) as cm:
                _fix_enum_field(x, choices)
        self.assertEqual(
            str(cm.exception), "Failed to convert option3 into one of the choices"
        )

    def test_fix_bool_field_false(self):
        x = "false"
        result = _fix_bool_field(x)
        self.assertFalse(result)

    def test_fix_str_field_invalid(self):
        x = object()
        try:
            _fix_str_field(x)
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Failed to convert <object object at 0x{:x}> into a string value".format(
                    id(x)
                ),
            )

    def test_fix_enum_field_valid(self):
        x = "option3"
        choices = ["option1", "option2"]
        with patch(
            "lionagi.libs.StringMatch.choose_most_similar", return_value="option1"
        ):
            result = _fix_enum_field(x, choices)
        self.assertEqual(result, "option1")

    def test_fix_enum_field_invalid(self):
        x = "option3"
        choices = ["option1", "option2"]
        with patch(
            "lionagi.libs.StringMatch.choose_most_similar",
            side_effect=ValueError("No match found"),
        ):
            with self.assertRaises(ValueError) as cm:
                _fix_enum_field(x, choices)
        self.assertEqual(
            str(cm.exception), "Failed to convert option3 into one of the choices"
        )


if __name__ == "__main__":
    unittest.main()
