"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re


class BaseToken:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"BaseDirectiveToken({self.type}, {self.value})"


class BaseTokenizer:
    TOKEN_TYPES = {
        "KEYWORD": r"\b(BEGIN|END|IF|ELSE|FOR|IN|TRY|EXCEPT|ENDIF|ENDFOR|ENDTRY|DO)\b",
        "OPERATOR": r"(==|!=|>=|<=|>|<|&&|\|\||!)",
        "FUNCTION_CALL": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b\((.*?)\)",
        "LITERAL": r'(\d+|\'.*?\'|".*?")',
        "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
        "PUNCTUATION": r"(;|,|\(|\))",
        "WHITESPACE": r"\s+",
    }

    def __init__(self, script):
        self.script = script
        self.tokens = []
        self.tokenize()

    @property
    def is_empty(self):
        return self.tokens == []

    def tokenize(self):
        position = 0
        while position < len(self.script):
            match = None
            for type_, pattern in self.TOKEN_TYPES.items():
                regex = re.compile(pattern)
                match = regex.match(self.script, position)
                if match:
                    if type_ != "WHITESPACE":  # Ignore whitespace
                        token = BaseToken(type_, match.group())
                        self.tokens.append(token)
                    position = match.end()  # Move past the matched token
                    break
            if not match:  # No match found, unrecognized token
                raise SyntaxError(f"Unexpected character: {self.script[position]}")
                # break

    def get_tokens(self):
        if self.is_empty:
            try:
                self.tokenize()
            except SyntaxError as e:
                print(e)
                return []
        return self.tokens
