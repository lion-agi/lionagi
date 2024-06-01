    def extract_code_blocks(code):
        code_blocks = []
        lines = code.split("\n")
        inside_code_block = False
        current_block = []

        for line in lines:
            if line.startswith("```"):
                if inside_code_block:
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                    inside_code_block = False
                else:
                    inside_code_block = True
            elif inside_code_block:
                current_block.append(line)

        if current_block:
            code_blocks.append("\n".join(current_block))

        return "\n\n".join(code_blocks)
