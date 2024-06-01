import unittest
from typing import Dict, List, Any
from lionagi.core.report.form import Form
from lionagi.core.report.report import Report
from lionagi.core.collections.abc import FieldError
from lionagi.core.rule.base import Rule
from lionagi.core.rule.rulebook import RuleBook
from lionagi.core.validator.validator import (
    Validator,
    _DEFAULT_RULEORDER,
    _DEFAULT_RULES,
)


class MockRule(Rule):
    def applies(self, *args, **kwargs):
        return True

    async def invoke(self, field, value, form, *args, **kwargs):
        if isinstance(value, int) and value < 0:
            raise ValueError(f"Field {field} cannot be negative.")
        return value

    async def validate(self, value: Any) -> Any:
        return value


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = Validator(
            rulebook=RuleBook(rules=_DEFAULT_RULES, ruleorder=_DEFAULT_RULEORDER)
        )
        self.form = Form(
            assignment="input1, input2 -> output",
            input_fields=["input1", "input2"],
            requested_fields=["output"],
        )
        self.form2 = Form(
            assignment="total_amount, bike_price -> repair_price",
            input_fields=["total_amount", "bike_price"],
            requested_fields=["repair_price"],
        )

    def test_initiate_rules(self):
        self.assertTrue(isinstance(self.validator.active_rules, dict))

    async def test_validate_field(self):
        self.validator.add_rule("mock_rule", MockRule)
        valid_value = await self.validator.validate_field("input1", 10, self.form)
        self.assertEqual(valid_value, 10)

        with self.assertRaises(FieldError):
            await self.validator.validate_field("input1", -5, self.form)

    async def test_validate_response(self):
        response = {"output": 20}
        validated_form = await self.validator.validate_response(self.form, response)
        self.assertEqual(validated_form.output, 20)

        response_str = "20"
        self.form.requested_fields = ["output"]
        validated_form = await self.validator.validate_response(self.form, response_str)
        self.assertEqual(validated_form.output, 20)

        with self.assertRaises(ValueError):
            await self.validator.validate_response(self.form, "invalid_response")

    async def test_validate_report(self):
        report = Report(assignment="a, b -> c", forms=[self.form])
        forms = [self.form, self.form2]
        validated_report = await self.validator.validate_report(report, forms)
        self.assertIsInstance(validated_report, Report)

    def test_add_rule(self):
        self.validator.add_rule("mock_rule", MockRule)
        self.assertIn("mock_rule", self.validator.active_rules)

    def test_remove_rule(self):
        self.validator.remove_rule("mock_rule")
        self.assertNotIn("mock_rule", self.validator.active_rules)

    def test_enable_rule(self):
        self.validator.enable_rule("mock_rule", enable=False)
        self.assertFalse(self.validator.active_rules["mock_rule"].enabled)
        self.validator.enable_rule("mock_rule", enable=True)
        self.assertTrue(self.validator.active_rules["mock_rule"].enabled)

    def test_disable_rule(self):
        self.validator.disable_rule("mock_rule")
        self.assertFalse(self.validator.active_rules["mock_rule"].enabled)

    def test_log_validation_attempt(self):
        result = {"output": 20}
        self.validator.log_validation_attempt(self.form, result)
        self.assertEqual(len(self.validator.validation_log), 1)

    def test_log_validation_error(self):
        self.validator.log_validation_error("input1", 10, "Error message")
        self.assertEqual(len(self.validator.validation_log), 1)

    def test_get_validation_summary(self):
        self.validator.log_validation_attempt(self.form, {"output": 20})
        self.validator.log_validation_error("input1", 10, "Error message")
        summary = self.validator.get_validation_summary()
        self.assertEqual(summary["total_attempts"], 2)
        self.assertEqual(len(summary["errors"]), 1)
        self.assertEqual(len(summary["successful_attempts"]), 1)


if __name__ == "__main__":
    unittest.main()
