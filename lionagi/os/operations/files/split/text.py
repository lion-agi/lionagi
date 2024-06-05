from typing import List
import re
import math
from .base import BaseSplitter


class TextSplitter(BaseSplitter):
    def __init__(
        self, separator: str = "\n\n", is_separator_regex: bool = False, **kwargs
    ):
        super().__init__(**kwargs)
        self.separator = separator
        self.is_separator_regex = is_separator_regex

    def split_text(self, text: str) -> List[str]:
        if self.is_separator_regex:
            splits = re.split(self.separator, text)
        else:
            splits = text.split(self.separator)

        return self._merge_splits(splits)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append("".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + len(self.separator)

        if current_chunk:
            merged_splits.append("".join(current_chunk))

        return merged_splits


import re
from typing import List, Optional, Dict, Any


class RecursiveCharacterSplitter(BaseSplitter):
    def __init__(self, separators: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if re.search(re.escape(sep), text):
                separator = sep
                new_separators = separators[separators.index(sep) + 1 :]
                break

        splits = re.split(re.escape(separator), text)
        good_splits = []
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    final_chunks.extend(self._merge_splits(good_splits))
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text(s, new_separators))
        if good_splits:
            final_chunks.extend(self._merge_splits(good_splits))
        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self.separators)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append("".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append("".join(current_chunk))

        return merged_splits



def chunk_by_chars(
    text: str, chunk_size: int, overlap: float, threshold: int
) -> list[str | None]:
    """
    Chunks the input text into smaller parts, with optional overlap and threshold for final chunk.

    Parameters:
        text (str): The input text to chunk.

        chunk_size (int): The size of each chunk.

        overlap (float): The amount of overlap between chunks.

        threshold (int): The minimum size of the final chunk.

    Returns:
        List[Union[str, None]]: A list of text chunks.

    Raises:
        ValueError: If an error occurs during chunking.
    """

    def _chunk_n1():
        return [text]

    def _chunk_n2():
        chunks = []
        chunks.append(text[: chunk_size + overlap_size])

        if len(text) - chunk_size > threshold:
            chunks.append(text[chunk_size - overlap_size :])
        else:
            return _chunk_n1()

        return chunks

    def _chunk_n3():
        chunks = []
        chunks.append(text[: chunk_size + overlap_size])
        for i in range(1, n_chunks - 1):
            start_idx = chunk_size * i - overlap_size
            end_idx = chunk_size * (i + 1) + overlap_size
            chunks.append(text[start_idx:end_idx])

        if len(text) - chunk_size * (n_chunks - 1) > threshold:
            chunks.append(text[chunk_size * (n_chunks - 1) - overlap_size :])
        else:
            chunks[-1] += text[chunk_size * (n_chunks - 1) + overlap_size :]

        return chunks

    try:
        if not isinstance(text, str):
            text = str(text)

        n_chunks = math.ceil(len(text) / chunk_size)
        overlap_size = int(overlap / 2)

        if n_chunks == 1:
            return _chunk_n1()

        elif n_chunks == 2:
            return _chunk_n2()

        elif n_chunks > 2:
            return _chunk_n3()

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")
