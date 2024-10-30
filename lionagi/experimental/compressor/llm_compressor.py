import asyncio
from time import time

import numpy as np

from lionagi import alcall
from lionagi.core.collections import iModel
from lionagi.libs.ln_convert import to_list
from lionagi.libs.ln_tokenize import TokenizeUtil

from .base import TokenCompressor

# inspired by LLMLingua, MIT License, Copyright (c) Microsoft Corporation.
# https://github.com/microsoft/LLMLingua


class LLMCompressor(TokenCompressor):

    def __init__(
        self,
        imodel: iModel = None,
        system_msg=None,
        tokenizer=None,  # must be a callable or object with a tokenize method
        splitter=None,  # must be a callable or object with a split/chunk/segment method
        target_ratio=0.2,
        n_samples=5,  # the cumulative samples to take in each perplexity calculation
        chunk_size=64,
        max_tokens_per_sample=80,
        min_compression_score=0,  # (0-1) the minimum score to consider for compression, 0 means all
        split_overlap=0,
        split_threshold=0,
        verbose=True,
    ):
        imodel = imodel or iModel(model="gpt-3.5-turbo", temperature=0.3)
        super().__init__(imodel=imodel, tokenizer=tokenizer, splitter=splitter)
        self.system_msg = (
            system_msg
            or "Concisely summarize and compress the information for storage:"
        )
        self.target_ratio = target_ratio
        self.n_samples = n_samples
        self.chunk_size = chunk_size
        self.max_tokens_per_sample = max_tokens_per_sample
        self.min_compression_score = min_compression_score
        self.verbose = verbose
        self.split_overlap = split_overlap
        self.split_threshold = split_threshold

    def tokenize(self, text, encoding_name=None, return_byte=False, **kwargs):
        """
        by default you can use `encoding_name` to be one of,
        ['gpt2', 'r50k_base', 'p50k_base', 'p50k_edit', 'cl100k_base', 'o200k_base']

        or you can use `encoding_model` that tiktoken supports in their mapping such as "gpt-4o"
        """
        if not self.tokenizer:
            return TokenizeUtil.tokenize(
                text,
                encoding_model=self.imodel.iModel_name,
                encoding_name=encoding_name,
                return_byte=return_byte,
            )

        if hasattr(self.tokenizer, "tokenize"):
            return self.tokenizer.tokenize(text, **kwargs)

        return self.tokenizer(text, **kwargs)

    def split(
        self,
        text,
        chunk_size=None,
        overlap=None,
        threshold=None,
        by_chars=False,
        return_tokens=False,
        return_byte=False,
        **kwargs,
    ):
        if not self.splitter:
            splitter = (
                TokenizeUtil.chunk_by_chars
                if by_chars
                else TokenizeUtil.chunk_by_tokens
            )
            return splitter(
                text,
                chunk_size or self.chunk_size,
                overlap or self.split_overlap,
                threshold or self.split_threshold,
                return_tokens=return_tokens,
                return_byte=return_byte,
            )

        a = [
            getattr(self.splitter, i, None)
            for i in ["split", "chunk", "segment"]
            if i is not None
        ][0]
        a = getattr(self.splitter, a)
        return a(text, **kwargs)

    async def rank_by_pplex(
        self,
        items: list,
        initial_text=None,
        cumulative=False,
        n_samples=None,
        **kwargs,
    ):
        """
        rank a list of items according to their perplexity
        an item can be a single token or a list of tokens

        kwargs: additional arguments to pass to the model
        """

        async def _get_item_perplexity(item):
            item = item if isinstance(item, list) else [item]
            item = (
                item[: self.max_tokens_per_sample]
                if len(item) > self.max_tokens_per_sample
                else item
            )
            return await self.imodel.compute_perplexity(
                initial_context=initial_text,
                tokens=item,
                n_samples=n_samples or self.n_samples,
                system_msg=self.system_msg,
                **kwargs,
            )

        if not isinstance(items, list):
            items = self.tokenize(items)

        if len(items) == 1:
            return [items]  # no need to rank a single item

        _segments = []
        _context = initial_text or ""
        _task = []

        if cumulative:
            for i in items:
                if isinstance(i, list):
                    _context += " " + " ".join(i).strip()
                else:
                    _context += " " + i.strip()

                _segments.append(_context)
        else:
            _segments = items

        for i in _segments:
            _task.append(asyncio.create_task(_get_item_perplexity(i)))

        results = await asyncio.gather(*_task)
        results = [(item, pplex) for item, pplex in zip(items, results)]
        return sorted(results, key=lambda x: x[1]["logprobs"], reverse=True)

    async def compress(
        self,
        text,
        target_ratio=None,
        initial_text=None,
        cumulative=False,
        split_kwargs=None,
        split_overlap=None,
        split_threshold=None,
        rank_by="perplexity",
        min_compression_score=None,
        verbose=True,
        **kwargs,
    ):
        start = time()
        if split_kwargs is None:
            split_kwargs = {}
            split_kwargs["chunk_size"] = self.max_tokens_per_sample
            split_kwargs["overlap"] = split_overlap or 0
            split_kwargs["threshold"] = split_threshold or 0

        len_tokens = len(self.tokenize(text))

        items = self.split(text, return_tokens=True, **split_kwargs)

        if rank_by == "perplexity":
            ranked_items = await self.rank_by_pplex(
                items=items,
                initial_text=initial_text,
                cumulative=cumulative,
                **kwargs,
            )

            prompt_tokens = sum(
                [i[1]["num_prompt_tokens"] for i in ranked_items]
            )

            num_completion_tokens = sum(
                [i[1]["num_completion_tokens"] for i in ranked_items]
            )

            price = (
                prompt_tokens * 0.5 / 1000000
                + num_completion_tokens * 1.5 / 1000000
            )

            selected_items = self.select_by_pplex(
                ranked_items=ranked_items,
                target_compression_ratio=target_ratio or self.target_ratio,
                original_length=len_tokens,
                min_pplex=min_compression_score or self.min_compression_score,
            )

            if verbose:
                msg = ""
                msg += f"Original Token number: {len_tokens}\n"

                def _f(i):
                    if isinstance(i, str):
                        i = self.tokenize(i)

                    if isinstance(i, list):
                        return len(to_list(i, dropna=True, flatten=True))

                len_ = sum([_f(i) for i in selected_items])
                msg += f"Selected Token number: {len_}\n"
                msg += f"Token Compression Ratio: {len_ / len_tokens:.03f}\n"
                msg += f"Compression Time: {time() - start:.04f} seconds\n"
                msg += f"Compression Model: {self.imodel.iModel_name}\n"
                msg += f"Compression Method: {rank_by}\n"
                msg += f"Compression Usage: ${price:.05f}\n"
                print(msg)

            a = "".join([i.strip() for i in selected_items]).strip()
            a = a.replace("\n\n", "")
            return a

        raise ValueError(f"Ranking method {rank_by} is not supported")

    def select_by_pplex(
        self,
        ranked_items,
        target_compression_ratio,
        original_length,
        min_pplex=None,
    ):
        min_pplex = min_pplex or 0

        desired_length = int(original_length * target_compression_ratio)

        items = []
        current_length = 0

        for item, info in ranked_items:
            if info["perplexity"] > min_pplex:
                item = self.tokenize(item) if isinstance(item, str) else item
                item = item if isinstance(item, list) else [item]
                item = to_list(item, dropna=True, flatten=True)
                if current_length + len(item) > desired_length:
                    break
                else:
                    current_length += len(item)
                    items.append("".join(item))

        return items
