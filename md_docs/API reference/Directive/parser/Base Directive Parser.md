
## Class: `BaseDirectiveParser`

**Description**:
`BaseDirectiveParser` is a base class designed for parsing tokens with support for lookahead, error recovery, and backtracking. It provides a framework for creating parsers for various directive-based languages.

**Attributes**:
- `tokens (List[BaseToken])`: A list of tokens to be parsed.
- `current_token_index (int)`: The index of the current token in the tokens list.
- `current_token (Optional[BaseToken])`: The current token being processed.

**Usage Examples**:
```python
tokenizer = BaseTokenizer("IF x > 10 THEN DO something ENDIF")
tokens = tokenizer.get_tokens()
parser = BaseDirectiveParser(tokens)
print(parser.current_token)
# Output: BaseToken(KEYWORD, IF)
```

### `__init__`

**Signature**:
```python
def __init__(self, tokens: List[BaseToken])
```

**Parameters**:
- `tokens (List[BaseToken])`: The list of tokens to be parsed.

**Description**:
Initializes a new instance of `BaseDirectiveParser`.

**Usage Examples**:
```python
tokenizer = BaseTokenizer("IF x > 10 THEN DO something ENDIF")
tokens = tokenizer.get_tokens()
parser = BaseDirectiveParser(tokens)
```

### `next_token`

**Signature**:
```python
def next_token() -> None
```

**Return Values**:
- `None`

**Description**:
Advances to the next token in the list.

**Usage Examples**:
```python
parser.next_token()
print(parser.current_token)
```

### `peek_next_token`

**Signature**:
```python
def peek_next_token(offset: int = 1) -> BaseToken | None
```

**Parameters**:
- `offset (int, optional)`: The number of tokens to look ahead. Defaults to `1`.

**Return Values**:
- `Optional[BaseToken]`: The token at the specified lookahead offset, or `None` if end of list.

**Description**:
Peeks at the next token without consuming it.

**Usage Examples**:
```python
next_token = parser.peek_next_token()
print(next_token)
```

### `skip_until`

**Signature**:
```python
def skip_until(token_types: List[str]) -> None
```

**Parameters**:
- `token_types (List[str])`: A list of token types to stop skipping.

**Return Values**:
- `None`

**Description**:
Skips tokens until a token of the specified type is found.

**Usage Examples**:
```python
parser.skip_until(['ENDIF', 'ELSE'])
```

### `mark`

**Signature**:
```python
def mark() -> int
```

**Return Values**:
- `int`: The current token index.

**Description**:
Marks the current position in the token list for potential backtracking.

**Usage Examples**:
```python
mark = parser.mark()
```

### `reset_to_mark`

**Signature**:
```python
def reset_to_mark(mark: int) -> None
```

**Parameters**:
- `mark (int)`: The token index to reset to.

**Return Values**:
- `None`

**Description**:
Resets the parser to a previously marked position.

**Usage Examples**:
```python
parser.reset_to_mark(mark)
```

### `skip_semicolon`

**Signature**:
```python
def skip_semicolon() -> None
```

**Return Values**:
- `None`

**Description**:
Skips a semicolon token if it is the current token.

**Usage Examples**:
```python
parser.skip_semicolon()
```

### `parse_expression`

**Signature**:
```python
def parse_expression() -> str
```

**Return Values**:
- `str`: The parsed expression as a string.

**Exceptions Raised**:
- `SyntaxError`: If a semicolon is not found at the end of the expression.

**Description**:
Parses an expression until a semicolon is encountered.

**Usage Examples**:
```python
expression = parser.parse_expression()
print(expression)
```

### `parse_if_block`

**Signature**:
```python
def parse_if_block() -> list
```

**Return Values**:
- `list`: The parsed block of statements as a list of strings.

**Description**:
Parses a block of statements for an IF condition.

**Usage Examples**:
```python
if_block = parser.parse_if_block()
print(if_block)
```

### `parse_if_statement`

**Signature**:
```python
def parse_if_statement() -> IfNode
```

**Return Values**:
- `IfNode`: The parsed IF statement as an `IfNode` object.

**Exceptions Raised**:
- `SyntaxError`: If the IF statement is not properly formed.

**Description**:
Parses an IF statement.

**Usage Examples**:
```python
if_statement = parser.parse_if_statement()
print(if_statement)
```

### `parse_for_statement`

**Signature**:
```python
def parse_for_statement() -> ForNode
```

**Return Values**:
- `ForNode`: The parsed FOR statement as a `ForNode` object.

**Exceptions Raised**:
- `SyntaxError`: If the FOR statement is not properly formed.

**Description**:
Parses a FOR statement.

**Usage Examples**:
```python
for_statement = parser.parse_for_statement()
print(for_statement)
```

### `parse_for_block`

**Signature**:
```python
def parse_for_block() -> list
```

**Return Values**:
- `list`: The parsed block of statements as a list of strings.

**Description**:
Parses a block of statements for a FOR loop.

**Usage Examples**:
```python
for_block = parser.parse_for_block()
print(for_block)
```

### `parse_try_statement`

**Signature**:
```python
def parse_try_statement() -> TryNode
```

**Return Values**:
- `TryNode`: The parsed TRY statement as a `TryNode` object.

**Exceptions Raised**:
- `SyntaxError`: If the TRY statement is not properly formed.

**Description**:
Parses a TRY statement.

**Usage Examples**:
```python
try_statement = parser.parse_try_statement()
print(try_statement)
```

### `parse_try_block`

**Signature**:
```python
def parse_try_block(stop_keyword: str) -> list
```

**Parameters**:
- `stop_keyword (str)`: The keyword that indicates the end of the block.

**Return Values**:
- `list`: The parsed block of statements as a list of strings.

**Description**:
Parses a block of statements for a TRY or EXCEPT clause.

**Usage Examples**:
```python
try_block = parser.parse_try_block("EXCEPT")
print(try_block)
```
