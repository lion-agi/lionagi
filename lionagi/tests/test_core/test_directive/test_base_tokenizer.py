from lionagi.core.directive.base.base_tokenizer import BaseTokenizer, BaseToken
import unittest


class TestBaseTokenizer(unittest.TestCase):
    def test_complex_script(self):
        script = """
        BEGIN; IF condition1 && condition2 || !condition3; DO action1(param1, param2); ENDIF;
        FOR item IN collections DO action2(item.param1, item.param2); ENDFOR; END;
        """
        tokenizer = BaseTokenizer(script)
        tokens = tokenizer.get_tokens()
        self.assertTrue(len(tokens) > 0)  # Basic check to ensure tokens are generated

    def test_function_calls(self):
        script = "action1(param1, param2);"
        tokenizer = BaseTokenizer(script)
        tokens = tokenizer.get_tokens()
        expected_types = ['FUNCTION_CALL', 'PUNCTUATION']
        token_types = [token.type for token in tokens]
        self.assertEqual(token_types, expected_types)

    def test_logical_operators(self):
        script = "condition1 && condition2 || !condition3"
        tokenizer = BaseTokenizer(script)
        tokens = tokenizer.get_tokens()
        expected_types = ['IDENTIFIER', 'OPERATOR', 'IDENTIFIER', 'OPERATOR', 'OPERATOR',
                          'IDENTIFIER']
        token_types = [token.type for token in tokens]
        self.assertEqual(token_types, expected_types)




# Running the updated tests
unittest.main(argv=[''], exit=False)
