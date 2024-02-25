import re

class BaseToken:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"











class BaseTokenizer:
    TOKEN_TYPES = {
        'KEYWORD': r'\b(DO|IF|ELIF|ELSE|FOR|IN|TRY|EXCEPT|END(IF|FOR|TRY)|BEGIN|END)\b',
        'OPERATOR': r'(==|!=|>=|<=|>|<|&&|\|\||!)',
        'LITERAL': r'(\d+|\'.*?\'|".*?")',
        'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
        'PUNCTUATION': r'(;|,|\(|\))',
        'WHITESPACE': r'\s+',
    }

    def __init__(self, script):
        self.script = script
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        position = 0
        while position < len(self.script):
            match = None
            for type_, pattern in self.TOKEN_TYPES.items():
                regex = re.compile(pattern)
                match = regex.match(self.script, position)
                if match:
                    if type_ != 'WHITESPACE':  # Ignore whitespace
                        token = BaseToken(type_, match.group())
                        self.tokens.append(token)
                    position = match.end()  # Move past the matched token
                    break
            if not match:  # No match found, unrecognized token
                raise SyntaxError(f"Unexpected character: {self.script[position]}")
                break  # Optionally, remove this line to raise the error instead of breaking the loop

    def get_tokens(self):
        return self.tokens
    
    
    

from typing import List, Dict, Union, Any
import unittest

class Token:
    """Represents a token in the parsing process.

    Attributes:
        type (str): The type of the token (e.g., 'KEYWORD', 'IDENTIFIER').
        value (str): The value of the token.
    """
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

class MockTokenizer:
    """A mock tokenizer for testing purposes.

    Attributes:
        tokens (List[Token]): A list of tokens to be processed.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = -1
        self.current_token = None
        self.next_token()

    def next_token(self) -> None:
        """Advances to the next token in the list."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

class BaseDirectiveParser:
    """Base class for directive parsers.

    Attributes:
        tokenizer (MockTokenizer): The tokenizer instance.
    """
    def __init__(self, tokenizer: MockTokenizer):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.current_token

    def next_token(self) -> None:
        """Advances to the next token using the tokenizer."""
        self.tokenizer.next_token()
        self.current_token = self.tokenizer.current_token

class ActionParser(BaseDirectiveParser):
    """Parses tools and parameters from tokens.

    This parser can handle nested tools and validate parameter types.

    Example:
        tokens = [
            Token('KEYWORD', 'DO'), Token('IDENTIFIER', 'actionWithNested'),
            Token('(', '('), Token('KEYWORD', 'DO'), Token('IDENTIFIER', 'nestedAction'),
            Token('(', '('), Token('IDENTIFIER', 'param'), Token(')', ')'), Token(')', ')'), Token(';', ';')
        ]
        tokenizer = MockTokenizer(tokens)
        parser = ActionParser(tokenizer)
        parsed_action = parser.parse_action()
        print(parsed_action)
        # Output: {'action': 'actionWithNested', 'parameters': [{'action': 'nestedAction', 'parameters': ['param']}]}
    """
    def parse_action(self) -> Dict[str, Any]:
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'DO':
            raise SyntaxError("Expected 'DO' keyword")
        self.next_token()  # Move past 'DO'

        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError("Expected an action name")
        action_name = self.current_token.value
        self.next_token()  # Move past action name

        parameters = []
        if self.current_token.value == '(':
            self.next_token()  # Move past '('
            while self.current_token.value != ')':
                if self.current_token.value == 'DO':
                    nested_action = self.parse_action()
                    parameters.append(nested_action)
                else:
                    parameters.append(self.current_token.value)
                    self.next_token()
                if self.current_token.value == ',':
                    self.next_token()  # Skip comma separator
            self.next_token()  # Move past ')'

        return {"action": action_name, "parameters": parameters}

    def validate_parameter_types(self, action: Dict[str, Any], expected_types: List[type]) -> bool:
        """Validates the types of parameters in an action.

        Args:
            action (Dict[str, Any]): The action containing parameters to validate.
            expected_types (List[type]): A list of expected types for the parameters.

        Returns:
            bool: True if parameters match expected types, False otherwise.

        Example:
            action = {'action': 'actionWithNested', 'parameters': [{'action': 'nestedAction', 'parameters': ['param']}]}
            is_valid = parser.validate_parameter_types(action, [dict])
            print(is_valid)  # Output: True
        """
        parameters = action['parameters']
        if len(parameters) != len(expected_types):
            return False
        for param, expected_type in zip(parameters, expected_types):
            if not isinstance(param, expected_type):
                return False
        return True

class TestActionParser(unittest.TestCase):
    """Unit tests for the ActionParser class."""

    def test_parse_action(self):
        tokens = [
            Token('KEYWORD', 'DO'), Token('IDENTIFIER', 'simpleAction'), Token(';', ';')
        ]
        tokenizer = MockTokenizer(tokens)
        parser = ActionParser(tokenizer)
        result = parser.parse_action()
        self.assertEqual(result, {'action': 'simpleAction', 'parameters': []})

    def test_validate_parameter_types(self):
        action = {'action': 'actionWithNested', 'parameters': [{'action': 'nestedAction', 'parameters': ['param']}]}
        parser = ActionParser(MockTokenizer([]))  # Empty tokenizer as it's not used in this test
        is_valid = parser.validate_parameter_types(action, [dict])
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()