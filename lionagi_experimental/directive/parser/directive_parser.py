from lionagi_experimental.directive.parser.base_directive_parser import BaseDirectiveParser
from lionagi_experimental.directive.schema.base_directive_node import IfNode, TryNode


class ActionParser(BaseDirectiveParser):
    def parse_action(self):
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'DO':
            raise SyntaxError("Expected 'DO' keyword")
        self.next_token()  # Move past 'DO'

        # Expecting an identifier for the action name
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError("Expected an action name")
        action_name = self.current_token.value
        self.next_token()  # Move past action name

        # Parse parameters if any, enclosed in parentheses
        parameters = []
        if self.current_token.value == '(':
            self.next_token()  # Move past '('
            while self.current_token.value != ')':
                parameters.append(self.current_token.value)  # Add parameter to list
                self.next_token()
                if self.current_token.value == ',':
                    self.next_token()  # Skip comma separator
            self.next_token()  # Move past ')'

        return {"action": action_name, "parameters": parameters}

    def parse_expression(self):
        # This is a highly simplified placeholder
        # A real implementation would need to handle operator precedence and associativity
        expression_parts = []
        while self.current_token and self.current_token.value not in {')', ';', 'ENDIF',
                                                                      'ENDFOR', 'ENDTRY'}:
            expression_parts.append(self.current_token.value)
            self.next_token()
        return " ".join(
            expression_parts)  # Returning a simple string representation for now

    def parse_block(self):
        block_nodes = []
        while self.current_token and self.current_token.value not in {'ENDIF', 'ENDFOR', 'ENDTRY'}:
            if self.current_token.value == 'DO':
                block_nodes.append(self.parse_action())
            elif self.current_token.value == 'IF':
                block_nodes.append(self.parse_if_statement())
            elif self.current_token.value == 'FOR':
                block_nodes.append(self.parse_for_loop())
            elif self.current_token.value == 'TRY':
                block_nodes.append(self.parse_try_except())
            else:
                # Handle unexpected tokens or end of block
                self.next_token()  # Skip unrecognized tokens or gracefully handle errors
        return block_nodes

    def parse_try_except(self):
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'TRY':
            raise SyntaxError("Expected TRY block")
        self.next_token()  # Move past TRY

        try_block = self.parse_block()  # Parse the block of tools within the TRY

        # Expecting 'EXCEPT' keyword
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'EXCEPT':
            raise SyntaxError("Expected 'EXCEPT' keyword in TRY block")
        self.next_token()  # Move past EXCEPT

        except_block = self.parse_block()  # Parse the block of tools within the EXCEPT

        return TryNode(try_block, except_block)

    def parse_action(self):
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

    def validate_parameter_types(self, action, expected_types):
        parameters = action['parameters']
        if len(parameters) != len(expected_types):
            return False
        for param, expected_type in zip(parameters, expected_types):
            if not isinstance(param, expected_type):
                return False
        return True





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

# Define the BaseParser class
class BaseParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = -1
        self.current_token = None
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
        
        condition = self.parse_expression()  # Placeholder for expression parsing logic
        
        true_block = self.parse_block()  # Placeholder for block parsing logic
        
        false_block = None
        if self.current_token and self.current_token.value == 'ELSE':
            self.next_token()  # Move past ELSE
            false_block = self.parse_block()  # Placeholder for block parsing logic
        
        return IfNode(condition, true_block, false_block)

    def parse_expression(self):
        expr = self.current_token.value
        self.next_token()  # Simulate parsing of an expression
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






# from lionagi.directive.base.base_directive_parser import BaseDirectiveParser
#
#
# class IfParser(BaseDirectiveParser):  # Extending the existing Parser class
#     def parse_block(self):
#         block = []
#         while self.current_token and self.current_token.value not in {'ENDIF', 'ENDFOR',
#                                                                       'ENDTRY'}:
#             if self.current_token.value == 'DO':
#                 block.append(self.parse_action())
#             elif self.current_token.value == 'IF':
#                 block.append(self.parse_if_statement())
#             # Add handling for other constructs (FOR, TRY, etc.) here
#             else:
#                 # This simplifies error handling for unrecognized statements
#                 raise SyntaxError(f"Unexpected token: {self.current_token.value}")
#             self.next_token()
#         return block
#
#     # Placeholder for parse_action method
#     def parse_action(self):
#         # Assuming tools are simple and directly followed by a semicolon
#         action = self.current_token.value
#         self.next_token()  # Move past the action
#         return action  # In a real scenario, this would return an ActionNode or similar
#
#     def parse_if_statement(self):
#         # Assume initial IF token checking is done
#         condition = self.parse_expression()
#         true_block = self.parse_block()
#         false_block = None
#         if self.current_token and self.current_token.value == 'ELSE':
#             self.next_token()  # Move past ELSE
#             false_block = self.parse_block()
#         return IfNode(condition, true_block, false_block)