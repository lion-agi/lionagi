import re
from typing import List
from .base import BaseSplitter


class LatexSplitter(BaseSplitter):
    def __init__(self, separators: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.separators = separators or [
            r"\\chapter{",
            r"\\section{",
            r"\\subsection{",
            r"\\subsubsection{",
            r"\\paragraph{",
            r"\\subparagraph{",
            r"\\begin{",
            r"\\end{",
        ]

    def split_text(self, text: str) -> List[str]:
        chunks = [text]
        for sep in self.separators:
            new_chunks = []
            for chunk in chunks:
                new_chunks.extend(re.split(sep, chunk))
            chunks = new_chunks

        return self._merge_splits(chunks)

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


import re
from typing import List, Optional


class RecursiveLatexSplitter(BaseSplitter):
    def __init__(self, separators: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.separators = separators or [
            r"\\chapter{",
            r"\\section{",
            r"\\subsection{",
            r"\\subsubsection{",
            r"\\paragraph{",
            r"\\subparagraph{",
            r"\\begin{",
            r"\\end{",
        ]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
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
                    final_chunks.extend(self._merge_splits(good_splits, separator))
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text(s, new_separators))
        if good_splits:
            final_chunks.extend(self._merge_splits(good_splits, separator))
        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self.separators)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append(separator.join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + len(separator)

        if current_chunk:
            merged_splits.append(separator.join(current_chunk))

        return merged_splits


# Example usage
latex_content = """
\\chapter{Introduction}
This is the introduction.
\\section{Background}
This is the background.
\\subsection{Details}
These are the details.
"""
splitter = RecursiveLatexSplitter(chunk_size=1000, chunk_overlap=0.1)
documents = splitter.create_documents([latex_content])
