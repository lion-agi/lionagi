# Example unittests for the BaseParser
import unittest
from lionagi.core.directive.base.base_tokenizer import BaseTokenizer
from lionagi.core.directive.base.base_parser import BaseParser, BaseToken, IfParser


class TestBaseParser(unittest.TestCase):
    def test_peek_next_token(self):
        tokens = [BaseToken("KEYWORD", "IF"), BaseToken("IDENTIFIER", "x")]
        parser = BaseParser(tokens)
        self.assertEqual(parser.peek_next_token().type, "IDENTIFIER")

    def test_skip_until(self):
        tokens = [BaseToken("KEYWORD", "IF"), BaseToken("IDENTIFIER", "x"),
                  BaseToken("KEYWORD", "THEN")]
        parser = BaseParser(tokens)
        parser.next_token()  # Advance to "x" to test skipping from there
        parser.skip_until(["KEYWORD"])
        self.assertEqual(parser.current_token.value, "THEN")


class TestIfParser(unittest.TestCase):
    def test_if_parser(self):
        script = "BEGIN; IF condition1; DO action1(param1); ELSE; DO action2(param2); ENDIF; END;"
        tokenizer = BaseTokenizer(script)
        tokens = tokenizer.get_tokens()
        parser = IfParser(tokens)
        result = parser.parse()

        # Using unittest assertions
        self.assertEqual(result['condition'], 'condition1', "Condition parsing failed")
        self.assertEqual(result['action1'], 'action1(param1)',
                         "Action1 parsing failed")
        self.assertEqual(result['action2'], 'action2(param2)',
                         "Action2 parsing failed")


if __name__ == "__main__":
    unittest.main()
