class Node:
    """Base class for all nodes in the abstract syntax tree (AST)."""
    pass


class IfNode(Node):
    """Represents an 'IF' statement in the AST."""

    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block


class ForNode(Node):
    """Represents a 'FOR' loop in the AST."""
    def __init__(self, iterator, collection, block):
        self.iterator = iterator
        self.collection = collection
        self.block = block


class TryNode(Node):
    """Represents a 'TRY-EXCEPT' block in the AST."""
    def __init__(self, try_block, except_block):
        self.try_block = try_block
        self.except_block = except_block



# Define the base Node class and specific AST node classes
class Node:
    """Base class for all nodes in the abstract syntax tree (AST)."""
    pass

class IfNode(Node):
    """Represents an 'IF' statement in the AST."""
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class ForNode(Node):
    """Represents a 'FOR' loop in the AST."""
    def __init__(self, iterator, collection, block):
        self.iterator = iterator
        self.collection = collection
        self.block = block

class TryNode(Node):
    """Represents a 'TRY-EXCEPT' block in the AST."""
    def __init__(self, try_block, except_block):
        self.try_block = try_block
        self.except_block = except_block

# Define the modified BaseParser class with expression caching
class BaseParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = -1
        self.current_token = None
        self.expression_cache = {}  # Cache for parsed expressions
        self.next_token()  # Initialize the first token

    def next_token(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None  # End of token list reached

    def parse_if_statement(self):
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IF':
            raise SyntaxError("Expected IF statement")
        self.next_token()  # Move past IF
        
        condition = self.parse_expression()  # Use caching for expression parsing
        
        true_block = self.parse_block()  # Placeholder for block parsing logic
        
        false_block = None
        if self.current_token and self.current_token.value == 'ELSE':
            self.next_token()  # Move past ELSE
            false_block = self.parse_block()  # Placeholder for block parsing logic
        
        return IfNode(condition, true_block, false_block)

    def parse_expression(self):
        # Check cache first
        if self.current_token_index in self.expression_cache:
            expr, next_index = self.expression_cache[self.current_token_index]
            self.current_token_index = next_index - 1  # Adjust index to continue parsing correctly
            self.next_token()  # Move to the next token after the cached expression
            return expr

        start_index = self.current_token_index
        expr = self.current_token.value
        self.next_token()  # Simulate parsing of an expression

        # Cache the result
        self.expression_cache[start_index] = (expr, self.current_token_index)
        return expr

    def parse_block(self):
        block = []
        while self.current_token and self.current_token.value != 'ENDIF':
            block.append(self.current_token.value)  # Simulate adding statements to the block
            self.next_token()
        self.next_token()  # Move past ENDIF
        return block

# Define a simple Token class
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# Define a simplified test case without 'ELSE'
tokens = [
    Token('KEYWORD', 'IF'),  # IF
    Token('IDENTIFIER', 'x'),  # condition
    Token('NUMBER', '1'),  # true block
    Token('KEYWORD', 'ENDIF')  # ENDIF
]

# Instantiate the parser and parse the if statement
parser = BaseParser(tokens)
if_node = parser.parse_if_statement()

# Print the parsed structure for verification
print(f"Condition: {if_node.condition}")
print(f"True block: {if_node.true_block}")
print(f"False block: {if_node.false_block}")