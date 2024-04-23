import unittest
from lionagi.experimental.form.form import Form

class TestForm(unittest.TestCase):

    def setUp(self):
        self.form = Form(assignment="input1, input2 -> output")

    def test_initialization_and_field_extraction(self):
        # Test initial field settings based on assignment parsing
        self.assertEqual(self.form.input_fields, ['input1', 'input2'])
        self.assertEqual(self.form.output_fields, ['output'])

    def test_fill_method_and_initial_state(self):
        # Initially, ensure no fields are set (we'll use to_dict to check state if properties aren't available)
        initial_state = self.form.to_dict()
        self.assertIsNone(initial_state.get('input1'))
        self.assertIsNone(initial_state.get('input2'))
        self.assertIsNone(initial_state.get('output'))

        # Fill input fields and check updates
        self.form.fill(input1=1, input2=2)
        state_after_fill = self.form.to_dict()
        self.assertEqual(state_after_fill.get('input1'), 1)
        self.assertEqual(state_after_fill.get('input2'), 2)

    def test_attempt_to_refill_input_fields(self):
        # Fill fields and attempt to refill them
        self.form.fill(input1=1, input2=2)
        self.form.fill(input1=10, input2=20)  # Attempt to change
        state_after_refill = self.form.to_dict()
        self.assertEqual(state_after_refill.get('input1'), 1, "Input1 should not change")
        self.assertEqual(state_after_refill.get('input2'), 2, "Input2 should not change")

    def test_fill_ignored_for_output_field(self):
        # Fill output should be ignored based on previous example behavior
        self.form.fill(output=3)
        self.form.fill(output=4)
        self.assertEqual(self.form.output, 3, "Output should not change")


if __name__ == '__main__':
    unittest.main()
