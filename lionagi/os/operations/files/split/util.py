import logging
from typing import Callable, List

log = logging.getLogger(__name__)


def trim_text(input_text: str, max_length: int) -> str:
    """Trim text to fit within the specified maximum length."""
    return input_text[:max_length]


def split_text_with_delimiter(input_text: str, delimiter: str) -> List[str]:
    """Split text with delimiter and keep the delimiter at the end of each split."""
    parts = input_text.split(delimiter)
    split_result = [
        delimiter + part if idx > 0 else part for idx, part in enumerate(parts)
    ]
    return [segment for segment in split_result if segment]


def create_splitter(
    delimiter: str, retain_delimiter: bool = True
) -> Callable[[str], List[str]]:
    """Create a function to split text by the specified delimiter."""
    if retain_delimiter:
        return lambda text: split_text_with_delimiter(text, delimiter)
    else:
        return lambda text: text.split(delimiter)


def character_splitter() -> Callable[[str], List[str]]:
    """Create a function to split text by each character."""
    return lambda text: list(text)


def sentence_splitter() -> Callable[[str], List[str]]:
    import nltk

    tokenizer = nltk.tokenize.PunktSentenceTokenizer()

    def split(input_text: str) -> List[str]:
        spans = list(tokenizer.span_tokenize(input_text))
        sentences = []
        for i, span in enumerate(spans):
            start_idx = span[0]
            end_idx = spans[i + 1][0] if i < len(spans) - 1 else len(input_text)
            sentences.append(input_text[start_idx:end_idx])
        return sentences

    return split


def regex_splitter(pattern: str) -> Callable[[str], List[str]]:
    """Create a function to split text by the specified regex pattern."""
    import re

    return lambda text: re.findall(pattern, text)


def phrase_splitter() -> Callable[[str], List[str]]:
    """Create a function to split text into phrases using a regex pattern.

    This regular expression will split the sentences into phrases,
    where each phrase is a sequence of one or more non-comma,
    non-period, and non-semicolon characters, followed by an optional comma,
    period, or semicolon. The regular expression will also capture the
    delimiters themselves as separate items in the list of phrases.
    """
    pattern = "[^,.;。]+[,.;。]?"
    return regex_splitter(pattern)
