import unittest
from lionagi import Form


class TestForm(unittest.TestCase):

    def setUp(self):
        self.form = Form(assignment="input1, input2 -> output")

    def test_initial_state(self):
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

    def test_fill_all_fields(self):
        self.form.fill(input1=1, input2=2)
        self.form.fill(output=3)
        self.assertTrue(self.form.filled)
        self.assertFalse(self.form.workable)
        self.assertEqual(self.form.work_fields, {"input1": 1, "input2": 2, "output": 3})

    def test_fill_once(self):
        self.form.fill(input1=1, input2=2)
        self.form.fill(output=3)
        with self.assertRaises(ValueError) as context:
            self.form.fill(input1=2, input2=3)
        self.assertTrue(
            "Form is filled, cannot be worked on again" in str(context.exception)
        )
        self.assertEqual(self.form.work_fields, {"input1": 1, "input2": 2, "output": 3})


if __name__ == "__main__":
    unittest.main()
