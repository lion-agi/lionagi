from typing import List


class ParagraphSplitter(BaseSplitter):
    def __init__(self, separator: str = "\n\n", **kwargs):
        super().__init__(**kwargs)
        self.separator = separator

    def split_text(self, text: str) -> List[str]:
        paragraphs = text.split(self.separator)
        return self._merge_splits(paragraphs)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append(self.separator.join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + len(self.separator)

        if current_chunk:
            merged_splits.append(self.separator.join(current_chunk))

        return merged_splits


# Example usage
text_content = "This is the first paragraph.\n\nThis is the second paragraph.\n\nThis is the third paragraph."
splitter = ParagraphSplitter(chunk_size=100, chunk_overlap=0.1)
documents = splitter.create_documents([text_content])
