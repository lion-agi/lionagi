import re
from typing import List


class RegexSplitter(BaseSplitter):
    def __init__(self, pattern: str, **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern

    def split_text(self, text: str) -> List[str]:
        splits = re.split(self.pattern, text)
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
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append("".join(current_chunk))

        return merged_splits
