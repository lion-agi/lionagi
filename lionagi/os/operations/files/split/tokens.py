import math
from typing import Callable, List, Optional
from ..tokenize.util import tokenize



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




def chunk_by_tokens(
    text: str,
    chunk_size: int,
    overlap: float,
    threshold: int,  # minimum size of the final chunk in number of tokens
    tokenizer=None,
    encoding_model=None,
    encoding_name=None,
    return_tokens=False,
    return_byte=False,
) -> list[str | None]:

    tokens = (tokenizer or tokenize)(
        text, encoding_model, encoding_name, return_byte=return_byte
    )

    n_chunks = math.ceil(len(tokens) / chunk_size)
    overlap_size = int(overlap * chunk_size / 2)
    residue = len(tokens) % chunk_size

    if n_chunks == 1:
        return text if not return_tokens else [tokens]

    elif n_chunks == 2:
        chunks = [tokens[: chunk_size + overlap_size]]
        if residue > threshold:
            chunks.append(tokens[chunk_size - overlap_size :])
            return (
                [" ".join(chunk).strip() for chunk in chunks]
                if not return_tokens
                else chunks
            )
        else:
            return text if not return_tokens else [tokens]

    elif n_chunks > 2:
        chunks = []
        chunks.append(tokens[: chunk_size + overlap_size])
        for i in range(1, n_chunks - 1):
            start_idx = chunk_size * i - overlap_size
            end_idx = chunk_size * (i + 1) + overlap_size
            chunks.append(tokens[start_idx:end_idx])

        if len(tokens) - chunk_size * (n_chunks - 1) > threshold:
            chunks.append(tokens[chunk_size * (n_chunks - 1) - overlap_size :])
        else:
            chunks[-1] += tokens[-residue:]

        return [" ".join(chunk) for chunk in chunks] if not return_tokens else chunks
