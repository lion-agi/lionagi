# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import math
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel


class Chunk(BaseModel):
    """
    Represents a partial slice of text read from [start_offset..end_offset).
    """

    start_offset: int | None = None
    end_offset: int | None = None
    chunk_content: str | None = None
    chunk_size: int | None = None
    chunk_id: int | None = None
    total_chunks: int | None = None
    metadata: dict[str, Any] | None = None


def chunk_by_chars(
    text: str, chunk_size: int = 2048, overlap: float = 0, threshold: int = 256
) -> list[tuple[str, int, int]]:
    """
    Split a string into chunks of approximately chunk_size in length,
    with optional overlap, returning a list of (subtext, start_offset, end_offset).

    The last chunk is appended only if it has at least 'threshold' characters,
    otherwise it is merged with the previous chunk.

    Returns:
        list[tuple[str, int, int]]: A list of (chunk_text, start_offset, end_offset)
    """
    if not text:
        return []

    n_chars = len(text)
    n_chunks = math.ceil(n_chars / chunk_size)
    overlap_size = int(chunk_size * overlap / 2)

    # Single chunk => no splitting
    if n_chunks == 1:
        return [(text, 0, n_chars)]

    # multiple chunks
    step = chunk_size - overlap_size
    chunks: list[tuple[str, int, int]] = []

    start = 0
    while start < n_chars:
        end = start + chunk_size + overlap_size
        if end > n_chars:
            end = n_chars
        chunk_text = text[start:end]
        chunks.append((chunk_text, start, end))
        start += step

    # check last chunk's threshold
    # If the last chunk is smaller than 'threshold',
    # merge it with the previous chunk
    if len(chunks) > 1:
        last_chunk_text, last_start, last_end = chunks[-1]
        if (last_end - last_start) < threshold:
            # merge into second-last chunk
            second_last_text, second_last_start, second_last_end = chunks[-2]
            merged_text = second_last_text + last_chunk_text
            merged = (merged_text, second_last_start, last_end)
            chunks[-2] = merged
            chunks.pop()  # remove last chunk

    return chunks


def chunk_by_tokens(
    tokens: list[str],
    chunk_size: int = 1024,
    overlap: float = 0,
    threshold: int = 128,
    return_tokens: bool = False,
) -> list[tuple[str, int, int]]:
    """
    Split a list of tokens into textual chunks with approximate chunk_size,
    returning a list of (subtext, start_offset, end_offset).
    The offsets here refer to *token-based* indexing for convenience.

    If the last chunk is smaller than `threshold` tokens, merge it
    with the previous chunk.

    Returns:
        List[Tuple[str, int, int]]: A list of (chunk_text, start_token_idx, end_token_idx).
    """
    if not tokens:
        return []

    n = len(tokens)
    n_chunks = math.ceil(n / chunk_size)
    overlap_size = int(chunk_size * overlap / 2)

    if n_chunks == 1:
        # Return entire list as single chunk
        text_chunk = tokens if return_tokens else " ".join(tokens)
        return [(text_chunk, 0, n)]

    step = chunk_size - overlap_size
    chunks: list[tuple[str, int, int]] = []

    start = 0
    while start < n:
        end = start + chunk_size + overlap_size
        if end > n:
            end = n
        sub_tokens = tokens[start:end]
        if return_tokens:
            chunk_text = sub_tokens
        else:
            chunk_text = " ".join(sub_tokens)
        chunks.append((chunk_text, start, end))
        start += step

    # If last chunk < threshold tokens => merge with second-last
    if len(chunks) > 1:
        last_text, last_start, last_end = chunks[-1]
        size_last = last_end - last_start
        if size_last < threshold:
            # merge
            sl_text, sl_start, sl_end = chunks[-2]
            if (
                return_tokens
                and isinstance(last_text, list)
                and isinstance(sl_text, list)
            ):
                merged_text = sl_text + last_text
            else:
                merged_text = f"{sl_text} {last_text}".strip()

            merged = (merged_text, sl_start, last_end)
            chunks[-2] = merged
            chunks.pop()

    return chunks


def chunk_content(
    content: str,
    chunk_by: Literal["chars", "tokens"] = "chars",
    tokenizer: Callable[[str], list[str]] = str.split,
    chunk_size: int = 1024,
    overlap: float = 0,
    threshold: int = 256,
    metadata: dict[str, Any] | None = None,
    return_tokens: bool = False,
    **tokenizer_kwargs: Any,
) -> list[Chunk]:
    """
    Split content into chunks using either character-based or token-based splitting,
    and produce a list of `Chunk` pydantic models, each containing offsets, content,
    size, id, total chunks, and any extra metadata.

    Args:
        content (str): The text to be chunked (if chunk_by='chars')
                       or the string to tokenize (if chunk_by='tokens').
        chunk_by (Literal['chars','tokens']): 'chars' => chunk by chars, 'tokens' => chunk by tokens
        tokenizer (Callable): A callable that takes the text and returns a list of tokens (only used if chunk_by='tokens').
        chunk_size (int): Target size for each chunk (characters or tokens).
        overlap (float): Fraction of overlap (0 <= overlap < 1).
        threshold (int): Minimum size for the last chunk. If smaller, merges with previous chunk.
        metadata (Dict[str,Any]|None): Additional metadata to attach to each chunk.
        return_tokens (bool): If chunk_by='tokens', return chunk as tokens or as a joined string.
        **tokenizer_kwargs: Extra args for your tokenizer function.

    Returns:
        List[Chunk]: A list of chunk objects with offsets, chunk content, total chunks, etc.

    Example:
        >>> text = \"This is a sample text for chunking.\"
        >>> # chunk by chars
        >>> chunk_list = chunk_content(text, chunk_by='chars', chunk_size=10, overlap=0.1)
        >>> # chunk by tokens
        >>> chunk_list = chunk_content(text, chunk_by='tokens', chunk_size=5, overlap=0.2)
    """
    metadata = metadata or {}
    if chunk_by == "tokens":
        # convert content to tokens
        tokens = tokenizer(content, **tokenizer_kwargs)
        subchunks = chunk_by_tokens(
            tokens=tokens,
            chunk_size=chunk_size,
            overlap=overlap,
            threshold=threshold,
            return_tokens=return_tokens,
        )
    else:
        # chunk by chars
        subchunks = chunk_by_chars(
            text=content,
            chunk_size=chunk_size,
            overlap=overlap,
            threshold=threshold,
        )

    total = len(subchunks)
    chunks_list: list[Chunk] = []

    for i, (chunk_text, start_off, end_off) in enumerate(subchunks):
        c = Chunk(
            start_offset=start_off,
            end_offset=end_off,
            chunk_content=(
                chunk_text
                if isinstance(chunk_text, str)
                else " ".join(chunk_text)
            ),
            chunk_size=(
                len(chunk_text)
                if isinstance(chunk_text, str)
                else sum(len(t) for t in chunk_text)
            ),
            chunk_id=i + 1,
            total_chunks=total,
            metadata=metadata,
        )
        chunks_list.append(c)

    return chunks_list
