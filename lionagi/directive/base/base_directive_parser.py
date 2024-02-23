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
        # This is a simplified placeholder implementation.
        # In a real parser, this method would be responsible for parsing expressions.
        expr = self.current_token.value
        self.next_token()  # Simulate parsing of an expression
        return expr

    def parse_block(self):
        # This is a simplified placeholder implementation.
        # In a real parser, this method would handle parsing a sequence of statements.
        block = []
        while self.current_token and self.current_token.value != 'ENDIF':
            block.append(self.current_token.value)  # Simulate adding statements to the block
            self.next_token()
        self.next_token()  # Move past ENDIF
        return block
