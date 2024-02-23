from lionagi.directive.base.base_directive_parser import BaseDirectiveParser


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

        try_block = self.parse_block()  # Parse the block of actions within the TRY

        # Expecting 'EXCEPT' keyword
        if self.current_token.type != 'KEYWORD' or self.current_token.value != 'EXCEPT':
            raise SyntaxError("Expected 'EXCEPT' keyword in TRY block")
        self.next_token()  # Move past EXCEPT

        except_block = self.parse_block()  # Parse the block of actions within the EXCEPT

        return TryNode(try_block, except_block)

#
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
#         # Assuming actions are simple and directly followed by a semicolon
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