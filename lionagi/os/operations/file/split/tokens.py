import logging
from typing import Callable, List, Optional


# Placeholder for the base splitter class (to be defined according to your specific base class requirements)
class BaseSplitter:
    def __init__(self, chunk_size: int = 100, chunk_overlap: int = 10, **kwargs):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_documents(self, texts: List[str]) -> List[List[str]]:
        documents = [self.split_text(text) for text in texts]
        return documents


# Simple Token Splitter class
class TokenSplitter(BaseSplitter):
    def __init__(self, tokenize_func: Callable[[str], List[str]], **kwargs):
        super().__init__(**kwargs)
        self.tokenize_func = tokenize_func

    def split_text(self, text: str) -> List[str]:
        tokens = self.tokenize_func(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            token_length = len(token)
            if current_length + token_length > self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [token]
                current_length = token_length
            else:
                current_chunk.append(token)
                current_length += token_length + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


# Example usage with a simple whitespace tokenizer
def whitespace_tokenizer(text: str) -> List[str]:
    return text.split()


# Metadata-aware Token Text Splitter
class TokenTextSplitter(BaseSplitter):
    def __init__(
        self,
        chunk_size: int = 100,
        chunk_overlap: int = 10,
        tokenizer: Optional[Callable] = None,
        separator: str = " ",
        backup_separators: Optional[List[str]] = ["\n"],
        **kwargs,
    ):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
        self.separator = separator
        self.backup_separators = backup_separators
        self.tokenizer = tokenizer or whitespace_tokenizer
        self._split_fns = [
            self._create_split_fn(sep)
            for sep in [separator] + (backup_separators or [])
        ]

    def _create_split_fn(self, sep: str) -> Callable[[str], List[str]]:
        return lambda text: text.split(sep)

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self.chunk_size)

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        if not text:
            return [text]

        tokens = self.tokenizer(text)
        if len(tokens) <= chunk_size:
            return [text]

        splits = self._apply_split_fns(text)
        return self._merge_splits(splits, chunk_size)

    def _apply_split_fns(self, text: str) -> List[str]:
        for split_fn in self._split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                return splits
        return list(text)  # fallback to character splitting if no splits are found

    def _merge_splits(self, splits: List[str], chunk_size: int) -> List[str]:
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(self.tokenizer(split))
            if current_length + split_length > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
