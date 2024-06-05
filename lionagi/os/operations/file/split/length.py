from typing import List


class LengthSplitter(BaseSplitter):
    def __init__(self, unit: str = "word", **kwargs):
        super().__init__(**kwargs)
        self.unit = unit

    def split_text(self, text: str) -> List[str]:
        if self.unit == "word":
            tokens = text.split()
        elif self.unit == "character":
            tokens = list(text)
        else:
            raise ValueError("Unit must be either 'word' or 'character'.")

        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            token_length = len(token)
            if current_length + token_length > self.chunk_size:
                if self.unit == "word":
                    chunks.append(" ".join(current_chunk))
                else:
                    chunks.append("".join(current_chunk))
                current_chunk = [token]
                current_length = token_length
            else:
                current_chunk.append(token)
                current_length += token_length + 1

        if current_chunk:
            if self.unit == "word":
                chunks.append(" ".join(current_chunk))
            else:
                chunks.append("".join(current_chunk))

        return chunks


# Example usage
text_content = (
    "This is a sentence. This is another sentence. This is yet another sentence."
)
splitter = LengthSplitter(chunk_size=20, chunk_overlap=0.1, unit="word")
documents = splitter.create_documents([text_content])
