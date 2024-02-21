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