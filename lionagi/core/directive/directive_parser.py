


class IfParser(BaseParser):
    def parse_if_statement(self):
        self.next_token()  # Move past IF
        self.skip_semicolon()

        condition = self.parse_condition()
        # Ensure we skip any semicolons after the condition
        while self.current_token and self.current_token.value == ';':
            self.next_token()

        if self.current_token.value != 'DO':
            raise SyntaxError("Expected DO after condition")
        self.next_token()  # Move past DO
        self.skip_semicolon()

        action1 = self.parse_action()
        self.skip_semicolon()

        action2 = None
        if self.current_token and self.current_token.value == 'ELSE':
            self.next_token()  # Move past ELSE
            self.skip_semicolon()
            action2 = self.parse_action()
            self.skip_semicolon()

        if self.current_token and self.current_token.value == 'ENDIF':
            self.next_token()  # Move past ENDIF
            self.skip_semicolon()
        else:
            raise SyntaxError("Expected ENDIF")

        return IfNode(condition, action1, action2)

    def parse_condition(self):
        condition_parts = re.split(r'(\|\||&&|!)', self.current_token.value)
        self.next_token()  # Move past condition
        return " ".join(condition_parts).strip()

    def parse_action(self):
        if self.current_token.value == 'IF':
            return self.parse_if_statement()  # Recursive call for nested IF
        else:
            action = self.current_token.value
            self.next_token()  # Move past action
            return action











#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# class BaseParser:
#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.current_token_index = -1
#         self.current_token = None
#         self.next_token()  # Initialize the first token
#
#     def next_token(self):
#         self.current_token_index += 1
#         if self.current_token_index < len(self.tokens):
#             self.current_token = self.tokens[self.current_token_index]
#         else:
#             self.current_token = None  # End of token list reached
#
#     def parse_expression(self):
#         expr = ""
#         while self.current_token and self.current_token.value != ';':
#             expr += self.current_token.value + " "
#             self.next_token()
#         # Expecting a semicolon at the end of the condition
#         if self.current_token.value != ';':
#             raise SyntaxError("Expected ';' at the end of the condition")
#         self.next_token()  # Move past the semicolon to the next part of the statement
#         return expr.strip()
#
#
# class IfParser(BaseParser):
#
#     def __init__(self, tokens):
#         super().__init__(tokens)
#
#     def parse_block(self):
#         block = []
#         # Parse the block until 'ELSE', 'ENDIF', ensuring not to include semicolons as part of the block
#         while self.current_token and self.current_token.value not in ('ENDIF', 'ELSE'):
#             if self.current_token.value == 'DO':
#                 self.next_token()  # Move past 'DO' to get to the action
#             block.append(self.current_token.value)  # Add the action to the block
#             self.next_token()  # Move to the next token, which could be a semicolon or the next action
#             if self.current_token.value == ';':
#                 self.next_token()  # Move past the semicolon
#         return block
#
#     def parse_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IF':
#             raise SyntaxError("Expected IF statement")
#         self.next_token()  # Skip 'IF'
#
#         condition = self.parse_expression()  # Now properly ends after the semicolon
#
#         true_block = []
#         if self.current_token.value == 'DO':
#             true_block = self.parse_block()  # Parse true block after 'DO'
#
#         false_block = None
#         if self.current_token and self.current_token.value == 'ELSE':
#             self.next_token()  # Skip 'ELSE', expect 'DO' next for the false block
#             if self.current_token.value != 'DO':
#                 raise SyntaxError("Expected 'DO' after 'ELSE'")
#             self.next_token()  # Skip 'DO'
#             false_block = self.parse_block()  # Parse false block
#
#         return IfNode(condition, true_block, false_block)
#
# class ForParser(BaseParser):
#     def __init__(self, tokens):
#         super().__init__(tokens)
#
#     def parse_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'FOR':
#             raise SyntaxError("Expected FOR statement")
#         self.next_token()  # Skip 'FOR'
#
#         # Parse the iterator variable
#         if self.current_token.type != 'IDENTIFIER':
#             raise SyntaxError("Expected iterator variable after FOR")
#         iterator = self.current_token.value
#         self.next_token()  # Move past the iterator variable
#
#         # Expect and skip 'IN' keyword
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IN':
#             raise SyntaxError("Expected 'IN' after iterator variable")
#         self.next_token()  # Move past 'IN'
#
#         # Parse the collection
#         if self.current_token.type not in ['IDENTIFIER', 'LITERAL']:
#             raise SyntaxError("Expected collection after 'IN'")
#         collection = self.current_token.value
#         self.next_token()  # Move past the collection
#
#         # Now, parse the block of statements to execute
#         true_block = self.parse_block()
#
#         # Construct and return a ForNode
#         return ForNode(iterator, collection, true_block)
#
#     def parse_block(self):
#         block = []
#         # Skip initial 'DO' if present
#         if self.current_token and self.current_token.value == 'DO':
#             self.next_token()
#
#         while self.current_token and self.current_token.value not in ('ENDFOR',):
#             if self.current_token.value == ';':
#                 # If a semicolon is encountered, skip it and move to the next token
#                 self.next_token()
#                 continue
#             # Add the current token to the block unless it's a 'DO' or ';'
#             if self.current_token.value != 'DO':
#                 block.append(self.current_token.value)
#             self.next_token()
#
#         # The loop exits when 'ENDFOR' is encountered; move past it for subsequent parsing
#         self.next_token()  # Skip 'ENDFOR'
#         return block
#
#
# class TryParser(BaseParser):
#     def __init__(self, tokens):
#         super().__init__(tokens)
#
#     def parse_try_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'TRY':
#             raise SyntaxError("Expected TRY statement")
#         self.next_token()  # Skip 'TRY'
#
#         try_block = self.parse_block('EXCEPT')  # Parse the try block until 'EXCEPT'
#
#         # Now expecting 'EXCEPT' keyword
#         if not (self.current_token and self.current_token.value == 'EXCEPT'):
#             raise SyntaxError("Expected 'EXCEPT' after try block")
#         self.next_token()  # Move past 'EXCEPT'
#
#         except_block = self.parse_block('ENDTRY')  # Parse the except block until 'ENDTRY'
#
#         # Ensure we are correctly positioned after 'ENDTRY'
#         if self.current_token and self.current_token.value != 'ENDTRY':
#             raise SyntaxError("Expected 'ENDTRY' at the end of except block")
#         self.next_token()  # Move past 'ENDTRY' for subsequent parsing
#
#         return TryNode(try_block, except_block)
#
#     def parse_block(self, stop_keyword):
#         block = []
#         while self.current_token and self.current_token.value != stop_keyword:
#             if self.current_token.value == 'DO':
#                 self.next_token()  # Move past 'DO' to get to the action
#             elif self.current_token.value == ';':
#                 self.next_token()  # Move past the semicolon
#                 continue  # Skip adding ';' to the block
#             else:
#                 block.append(self.current_token.value)  # Add the action to the block
#                 self.next_token()
#
#         return block
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# from lionagi_experimental.directive.parser.base_directive_parser import \
#     BaseDirectiveParser
# from lionagi_experimental.directive.schema.base_directive_node import IfNode, TryNode
#
#
# class ActionParser(BaseDirectiveParser):
#     def parse_action(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'DO':
#             raise SyntaxError("Expected 'DO' keyword")
#         self.next_token()  # Move past 'DO'
#
#         # Expecting an identifier for the action name
#         if self.current_token.type != 'IDENTIFIER':
#             raise SyntaxError("Expected an action name")
#         action_name = self.current_token.value
#         self.next_token()  # Move past action name
#
#         # Parse parameters if any, enclosed in parentheses
#         parameters = []
#         if self.current_token.value == '(':
#             self.next_token()  # Move past '('
#             while self.current_token.value != ')':
#                 parameters.append(self.current_token.value)  # Add parameter to list
#                 self.next_token()
#                 if self.current_token.value == ',':
#                     self.next_token()  # Skip comma separator
#             self.next_token()  # Move past ')'
#
#         return {"action": action_name, "parameters": parameters}
#
#     def parse_expression(self):
#         # This is a highly simplified placeholder
#         # A real implementation would need to handle operator precedence and associativity
#         expression_parts = []
#         while self.current_token and self.current_token.value not in {')', ';', 'ENDIF',
#                                                                       'ENDFOR', 'ENDTRY'}:
#             expression_parts.append(self.current_token.value)
#             self.next_token()
#         return " ".join(
#             expression_parts)  # Returning a simple string representation for now
#
#     def parse_block(self):
#         block_nodes = []
#         while self.current_token and self.current_token.value not in {'ENDIF', 'ENDFOR',
#                                                                       'ENDTRY'}:
#             if self.current_token.value == 'DO':
#                 block_nodes.append(self.parse_action())
#             elif self.current_token.value == 'IF':
#                 block_nodes.append(self.parse_if_statement())
#             elif self.current_token.value == 'FOR':
#                 block_nodes.append(self.parse_for_loop())
#             elif self.current_token.value == 'TRY':
#                 block_nodes.append(self.parse_try_except())
#             else:
#                 # Handle unexpected tokens or end of block
#                 self.next_token()  # Skip unrecognized tokens or gracefully handle errors
#         return block_nodes
#
#     def parse_try_except(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'TRY':
#             raise SyntaxError("Expected TRY block")
#         self.next_token()  # Move past TRY
#
#         try_block = self.parse_block()  # Parse the block of tools within the TRY
#
#         # Expecting 'EXCEPT' keyword
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'EXCEPT':
#             raise SyntaxError("Expected 'EXCEPT' keyword in TRY block")
#         self.next_token()  # Move past EXCEPT
#
#         except_block = self.parse_block()  # Parse the block of tools within the EXCEPT
#
#         return TryNode(try_block, except_block)
#
#     def parse_action(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'DO':
#             raise SyntaxError("Expected 'DO' keyword")
#         self.next_token()  # Move past 'DO'
#
#         if self.current_token.type != 'IDENTIFIER':
#             raise SyntaxError("Expected an action name")
#         action_name = self.current_token.value
#         self.next_token()  # Move past action name
#
#         parameters = []
#         if self.current_token.value == '(':
#             self.next_token()  # Move past '('
#             while self.current_token.value != ')':
#                 if self.current_token.value == 'DO':
#                     nested_action = self.parse_action()
#                     parameters.append(nested_action)
#                 else:
#                     parameters.append(self.current_token.value)
#                     self.next_token()
#                 if self.current_token.value == ',':
#                     self.next_token()  # Skip comma separator
#             self.next_token()  # Move past ')'
#
#         return {"action": action_name, "parameters": parameters}
#
#     def validate_parameter_types(self, action, expected_types):
#         parameters = action['parameters']
#         if len(parameters) != len(expected_types):
#             return False
#         for param, expected_type in zip(parameters, expected_types):
#             if not isinstance(param, expected_type):
#                 return False
#         return True
#
#
# class Node:
#     """Base class for all nodes in the abstract syntax tree (AST)."""
#     pass
#
#
# class IfNode(Node):
#     """Represents an 'IF' statement in the AST."""
#
#     def __init__(self, condition, true_block, false_block=None):
#         self.condition = condition
#         self.true_block = true_block
#         self.false_block = false_block
#
#
# class ForNode(Node):
#     """Represents a 'FOR' loop in the AST."""
#
#     def __init__(self, iterator, collection, block):
#         self.iterator = iterator
#         self.collection = collection
#         self.block = block
#
#
# class TryNode(Node):
#     """Represents a 'TRY-EXCEPT' block in the AST."""
#
#     def __init__(self, try_block, except_block):
#         self.try_block = try_block
#         self.except_block = except_block
#
#
# # Define the BaseParser class
# class BaseParser:
#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.current_token_index = -1
#         self.current_token = None
#         self.next_token()  # Initialize the first token
#
#     def next_token(self):
#         self.current_token_index += 1
#         if self.current_token_index < len(self.tokens):
#             self.current_token = self.tokens[self.current_token_index]
#         else:
#             self.current_token = None  # End of token list reached
#
#     def parse_if_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IF':
#             raise SyntaxError("Expected IF statement")
#         self.next_token()  # Move past IF
#
#         condition = self.parse_expression()  # Placeholder for expression parsing logic
#
#         true_block = self.parse_block()  # Placeholder for block parsing logic
#
#         false_block = None
#         if self.current_token and self.current_token.value == 'ELSE':
#             self.next_token()  # Move past ELSE
#             false_block = self.parse_block()  # Placeholder for block parsing logic
#
#         return IfNode(condition, true_block, false_block)
#
#     def parse_expression(self):
#         expr = self.current_token.value
#         self.next_token()  # Simulate parsing of an expression
#         return expr
#
#     def parse_block(self):
#         block = []
#         while self.current_token and self.current_token.value != 'ENDIF':
#             block.append(
#                 self.current_token.value)  # Simulate adding statements to the block
#             self.next_token()
#         self.next_token()  # Move past ENDIF
#         return block
#
#
# # Define a simple BaseDirectiveToken class
# class Token:
#     def __init__(self, type, value):
#         self.type = type
#         self.value = value
#
#
# # Define a simplified test case without 'ELSE'
# tokens = [
#     Token('KEYWORD', 'IF'),  # IF
#     Token('IDENTIFIER', 'x'),  # condition
#     Token('NUMBER', '1'),  # true block
#     Token('KEYWORD', 'ENDIF')  # ENDIF
# ]
#
# # Instantiate the parser and parse the if statement
# parser = BaseParser(tokens)
# if_node = parser.parse_if_statement()
#
# # Print the parsed structure for verification
# print(f"Condition: {if_node.condition}")
# print(f"True block: {if_node.true_block}")
# print(f"False block: {if_node.false_block}")
#
#
# # from lionagi.directive.base.base_directive_parser import BaseDirectiveParser
# #
# #
# # class IfParser(BaseDirectiveParser):  # Extending the existing Parser class
# #     def parse_block(self):
# #         block = []
# #         while self.current_token and self.current_token.value not in {'ENDIF', 'ENDFOR',
# #                                                                       'ENDTRY'}:
# #             if self.current_token.value == 'DO':
# #                 block.append(self.parse_action())
# #             elif self.current_token.value == 'IF':
# #                 block.append(self.parse_if_statement())
# #             # Add handling for other constructs (FOR, TRY, etc.) here
# #             else:
# #                 # This simplifies error handling for unrecognized statements
# #                 raise SyntaxError(f"Unexpected token: {self.current_token.value}")
# #             self.next_token()
# #         return block
# #
# #     # Placeholder for parse_action method
# #     def parse_action(self):
# #         # Assuming tools are simple and directly followed by a semicolon
# #         action = self.current_token.value
# #         self.next_token()  # Move past the action
# #         return action  # In a real scenario, this would return an ActionNode or similar
# #
# #     def parse_if_statement(self):
# #         # Assume initial IF token checking is done
# #         condition = self.parse_expression()
# #         true_block = self.parse_block()
# #         false_block = None
# #         if self.current_token and self.current_token.value == 'ELSE':
# #             self.next_token()  # Move past ELSE
# #             false_block = self.parse_block()
# #         return IfNode(condition, true_block, false_block)
#
#
# class BaseDirectiveParser:
#     """Base class for directive parsers.
#
#     Attributes:
#         tokenizer (MockTokenizer): The tokenizer instance.
#     """
#
#     def __init__(self, tokenizer: MockTokenizer):
#         self.tokenizer = tokenizer
#         self.current_token = self.tokenizer.current_token
#
#     def next_token(self) -> None:
#         """Advances to the next token using the tokenizer."""
#         self.tokenizer.next_token()
#         self.current_token = self.tokenizer.current_token
#
#
# class ActionParser(BaseDirectiveParser):
#     """Parses tools and parameters from tokens.
#
#     This parser can handle nested tools and validate parameter types.
#
#     Example:
#         tokens = [
#             BaseDirectiveToken('KEYWORD', 'DO'), BaseDirectiveToken('IDENTIFIER', 'actionWithNested'),
#             BaseDirectiveToken('(', '('), BaseDirectiveToken('KEYWORD', 'DO'), BaseDirectiveToken('IDENTIFIER', 'nestedAction'),
#             BaseDirectiveToken('(', '('), BaseDirectiveToken('IDENTIFIER', 'param'), BaseDirectiveToken(')', ')'), BaseDirectiveToken(')', ')'), BaseDirectiveToken(';', ';')
#         ]
#         tokenizer = MockTokenizer(tokens)
#         parser = ActionParser(tokenizer)
#         parsed_action = parser.parse_action()
#         print(parsed_action)
#         # Output: {'action': 'actionWithNested', 'parameters': [{'action': 'nestedAction', 'parameters': ['param']}]}
#     """
#
#     def parse_action(self) -> Dict[str, Any]:
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'DO':
#             raise SyntaxError("Expected 'DO' keyword")
#         self.next_token()  # Move past 'DO'
#
#         if self.current_token.type != 'IDENTIFIER':
#             raise SyntaxError("Expected an action name")
#         action_name = self.current_token.value
#         self.next_token()  # Move past action name
#
#         parameters = []
#         if self.current_token.value == '(':
#             self.next_token()  # Move past '('
#             while self.current_token.value != ')':
#                 if self.current_token.value == 'DO':
#                     nested_action = self.parse_action()
#                     parameters.append(nested_action)
#                 else:
#                     parameters.append(self.current_token.value)
#                     self.next_token()
#                 if self.current_token.value == ',':
#                     self.next_token()  # Skip comma separator
#             self.next_token()  # Move past ')'
#
#         return {"action": action_name, "parameters": parameters}
#
#     def validate_parameter_types(self, action: Dict[str, Any],
#                                  expected_types: List[type]) -> bool:
#         """Validates the types of parameters in an action.
#
#         Args:
#             action (Dict[str, Any]): The action containing parameters to validate.
#             expected_types (List[type]): A list of expected types for the parameters.
#
#         Returns:
#             bool: True if parameters match expected types, False otherwise.
#
#         Example:
#             action = {'action': 'actionWithNested', 'parameters': [{'action': 'nestedAction', 'parameters': ['param']}]}
#             is_valid = parser.validate_parameter_types(action, [dict])
#             print(is_valid)  # Output: True
#         """
#         parameters = action['parameters']
#         if len(parameters) != len(expected_types):
#             return False
#         for param, expected_type in zip(parameters, expected_types):
#             if not isinstance(param, expected_type):
#                 return False
#         return True
#
#
# class BaseParser:
#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.current_token_index = -1
#         self.current_token = None
#         self.expression_cache = {}  # Cache for parsed expressions
#         self.next_token()  # Initialize the first token
#
#     def next_token(self):
#         self.current_token_index += 1
#         if self.current_token_index < len(self.tokens):
#             self.current_token = self.tokens[self.current_token_index]
#         else:
#             self.current_token = None  # End of token list reached
#
#     def parse_if_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IF':
#             raise SyntaxError("Expected IF statement")
#         self.next_token()  # Move past IF
#
#         condition = self.parse_expression()  # Use caching for expression parsing
#
#         true_block = self.parse_block()  # Placeholder for block parsing logic
#
#         false_block = None
#         if self.current_token and self.current_token.value == 'ELSE':
#             self.next_token()  # Move past ELSE
#             false_block = self.parse_block()  # Placeholder for block parsing logic
#
#         return IfNode(condition, true_block, false_block)
#
#     def parse_expression(self):
#         # Check cache first
#         if self.current_token_index in self.expression_cache:
#             expr, next_index = self.expression_cache[self.current_token_index]
#             self.current_token_index = next_index - 1  # Adjust index to continue parsing correctly
#             self.next_token()  # Move to the next token after the cached expression
#             return expr
#
#         start_index = self.current_token_index
#         expr = self.current_token.value
#         self.next_token()  # Simulate parsing of an expression
#
#         # Cache the result
#         self.expression_cache[start_index] = (expr, self.current_token_index)
#         return expr
#
#     def parse_block(self):
#         block = []
#         while self.current_token and self.current_token.value != 'ENDIF':
#             block.append(
#                 self.current_token.value)  # Simulate adding statements to the block
#             self.next_token()
#         self.next_token()  # Move past ENDIF
#         return block
#
#
# from lionagi_experimental.directive.schema.base_directive_node import IfNode
#
#
# class BaseDirectiveParser:
#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.current_token_index = -1
#         self.current_token = None
#         self.next_token()  # Initialize the first token
#
#     def next_token(self):
#         self.current_token_index += 1
#         if self.current_token_index < len(self.tokens):
#             self.current_token = self.tokens[self.current_token_index]
#         else:
#             self.current_token = None  # End of token list reached
#
#     def parse_if_statement(self):
#         if self.current_token.type != 'KEYWORD' or self.current_token.value != 'IF':
#             raise SyntaxError("Expected IF statement")
#         self.next_token()  # Move past IF
#
#         condition = self.parse_expression()  # Placeholder for expression parsing logic
#
#         true_block = self.parse_block()  # Placeholder for block parsing logic
#
#         false_block = None
#         if self.current_token and self.current_token.value == 'ELSE':
#             self.next_token()  # Move past ELSE
#             false_block = self.parse_block()  # Placeholder for block parsing logic
#
#         return IfNode(condition, true_block, false_block)
#
#     def parse_expression(self):
#         # This is a simplified placeholder implementation.
#         # In a real parser, this method would be responsible for parsing expressions.
#         expr = self.current_token.value
#         self.next_token()  # Simulate parsing of an expression
#         return expr
#
#     def parse_block(self):
#         # This is a simplified placeholder implementation.
#         # In a real parser, this method would handle parsing a sequence of statements.
#         block = []
#         while self.current_token and self.current_token.value != 'ENDIF':
#             block.append(
#                 self.current_token.value)  # Simulate adding statements to the block
#             self.next_token()
#         self.next_token()  # Move past ENDIF
#         return block