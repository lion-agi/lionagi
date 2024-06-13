import unittest
from lionagi.core.report.form import Form
from lionagi.core.report.report import Report


class TestForm(unittest.TestCase):

    def setUp(self):
        self.form = Form(assignment="input1, input2 -> output")

    def test_initial_fields(self):
        self.assertEqual(self.form.input_fields, ["input1", "input2"])
        self.assertEqual(self.form.requested_fields, ["output"])
        self.assertFalse(self.form.workable)
        self.assertFalse(self.form.filled)
        self.assertEqual(
            self.form.work_fields, {"input1": None, "input2": None, "output": None}
        )

    def test_fill_input_fields(self):
        self.form.fill(input1=1, input2=2)
        self.assertTrue(self.form.workable)
        self.assertFalse(self.form.filled)
        self.assertEqual(
            self.form.work_fields, {"input1": 1, "input2": 2, "output": None}
        )

    def test_fill_output_field(self):
        self.form.fill(input1=1, input2=2)
        self.form.fill(output=3)
        self.assertTrue(self.form.filled)
        self.assertEqual(self.form.work_fields, {"input1": 1, "input2": 2, "output": 3})
        self.assertFalse(self.form.workable)

    def test_fill_again_raises_error(self):
        self.form.fill(input1=1, input2=2, output=3)
        with self.assertRaises(ValueError):
            self.form.fill(input1=2, input2=3)


class TestReport(unittest.TestCase):

    def setUp(self):
        self.report = Report(assignment="a, b -> c")

    def test_initial_fields(self):
        self.assertEqual(self.report.input_fields, ["a", "b"])
        self.assertEqual(self.report.requested_fields, ["c"])
        self.assertEqual(self.report.work_fields, {"a": None, "b": None, "c": None})
        self.assertFalse(self.report.filled)
        self.assertFalse(self.report.workable)

    def test_fill_input_fields(self):
        self.report.fill(a=3, b=4)
        self.assertEqual(self.report.work_fields, {"a": 3, "b": 4, "c": None})
        self.assertTrue(self.report.workable)

    def test_fill_output_field(self):
        self.report.fill(a=3, b=4)
        self.report.fill(c=4)
        self.assertEqual(self.report.work_fields, {"a": 3, "b": 4, "c": 4})
        self.assertTrue(self.report.filled)
        self.assertFalse(self.report.workable)

    def test_next_forms_none(self):
        self.assertIsNone(self.report.next_forms())

    def test_complex_assignment(self):
        self.report = Report(
            assignment="a, b -> h",
            form_assignments=[
                "a, b -> c",
                "a -> e",
                "b -> f",
                "c -> g",
                "e, f, g -> h",
            ],
            a=3,
            b=4,
        )
        self.assertEqual(
            self.report.work_fields,
            {
                "a": None,
                "b": None,
                "c": None,
                "e": None,
                "f": None,
                "g": None,
                "h": None,
            },
        )
        self.report.fill(c=5, e=6, f=7, g=8, h=10)
        self.assertEqual(
            self.report.work_fields,
            {"a": None, "b": None, "c": 5, "e": 6, "f": 7, "g": 8, "h": 10},
        )
        self.assertFalse(self.report.filled)
        self.assertFalse(self.report.workable)
        with self.assertRaises(ValueError):
            self.report.fill(c="xx", e="yy")


if __name__ == "__main__":
    unittest.main()
