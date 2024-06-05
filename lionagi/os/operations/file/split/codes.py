import re
from typing import List, Optional


class CodeChunker:
    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: float,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\nclass ",
            "\ndef ",
            "\nif ",
            "\nfor ",
            "\nwhile ",
            "\n",
        ]

    def split_text(self, text: str) -> List[str]:
        chunks = [text]
        for sep in self.separators:
            new_chunks = []
            for chunk in chunks:
                new_chunks.extend(re.split(sep, chunk))
            chunks = new_chunks
        return self._merge_chunks(chunks)

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        merged_chunks = []
        current_chunk = []
        current_length = 0

        for chunk in chunks:
            chunk_length = len(chunk)
            if current_length + chunk_length > self.chunk_size:
                merged_chunks.append("".join(current_chunk))
                current_chunk = [chunk]
                current_length = chunk_length
            else:
                current_chunk.append(chunk)
                current_length += chunk_length + 1

        if current_chunk:
            merged_chunks.append("".join(current_chunk))

        return merged_chunks


# Example usage
splitter = CodeChunker(chunk_size=1500, chunk_overlap=0.1)
documents = splitter.split_text(
    "def foo():\n    pass\nclass Bar:\n    def baz():\n        pass\n"
)


class RecursiveCodeChunker(CodeChunker):
    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: float,
        separators: Optional[List[str]] = None,
    ):
        super().__init__(chunk_size, chunk_overlap, separators)
        self.separators = separators or [
            r"\nclass ",
            r"\ndef ",
            r"\nif ",
            r"\nfor ",
            r"\nwhile ",
            r"\ntry ",
            r"\nexcept ",
            r"\nwith ",
            r"\n",
        ]

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for sep in separators:
            if re.search(sep, text):
                separator = sep
                new_separators = separators[separators.index(sep) + 1 :]
                break

        splits = re.split(separator, text)
        good_splits = []

        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    final_chunks.extend(self._merge_chunks(good_splits))
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text_recursive(s, new_separators))

        if good_splits:
            final_chunks.extend(self._merge_chunks(good_splits))

        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_text_recursive(text, self.separators)


# Example usage
code_content = """
def foo():
    pass

class Bar:
    def baz(self):
        pass

if __name__ == "__main__":
    foo()
"""
splitter = RecursiveCodeChunker(chunk_size=100, chunk_overlap=0.1)
documents = splitter.split_text(code_content)
