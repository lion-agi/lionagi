import asyncio
from dataclasses import dataclass
from timeit import default_timer as timer

import numpy as np
from pydantic import BaseModel

from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.service.endpoints.base import APICalling
from lionagi.service.imodel import iModel
from lionagi.utils import alcall, lcall, to_dict, to_list


@dataclass
class PerplexityScores:
    """
    Stores logprobs, tokens, and derived perplexity from a completion response.
    """

    completion_response: BaseModel | dict
    original_tokens: list[str]
    n_samples: int

    @property
    def logprobs(self) -> list[float]:
        """Return list of logprobs extracted from the model response."""
        return [i["logprob"] for i in self.perplexity_scores]

    @property
    def perplexity(self) -> float:
        """
        e^(mean logprob), if logprobs exist. Fallback to 1.0 if empty.
        """
        if not self.logprobs:
            return 1.0
        return np.exp(np.mean(self.logprobs))

    @property
    def perplexity_scores(self) -> list[dict]:
        """
        Return [{'token': ..., 'logprob': ...}, ...].
        Handles two possible logprob structures:
          - "tokens" + "token_logprobs"
          - "content" (older style)
        """
        outs = []
        try:
            if isinstance(self.completion_response, dict):
                log_prob = self.completion_response["choices"][0]["logprobs"]
            else:
                # Pydantic or other object
                log_prob = self.completion_response.choices[0].logprobs
        except Exception:
            return outs

        if not log_prob:
            return outs

        if "tokens" in log_prob and "token_logprobs" in log_prob:
            # OpenAI style logprobs
            for token, lp in zip(
                log_prob["tokens"], log_prob["token_logprobs"]
            ):
                outs.append({"token": token, "logprob": lp})
        elif "content" in log_prob:
            # Old style logprobs
            for item in log_prob["content"]:
                outs.append(
                    {"token": item["token"], "logprob": item["logprob"]}
                )
        return outs

    def to_dict(self) -> dict:
        """
        Construct a dictionary representation, including perplexity, usage, etc.
        """
        # usage info
        usage = {}
        if isinstance(self.completion_response, dict):
            usage = self.completion_response.get("usage", {})
        else:
            usage = to_dict(self.completion_response.usage)

        return {
            "perplexity": self.perplexity,
            "original_tokens": self.original_tokens,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def to_log(self) -> Log:
        """
        Return a Log object for convenience.
        """
        return Log(content=self.to_dict())


async def compute_perplexity(
    chat_model: iModel,
    initial_context: str = None,
    tokens: list[str] = None,
    system: str = None,
    n_samples: int = 1,
    use_residue: bool = True,
    **kwargs,
) -> list[PerplexityScores]:
    """
    Splits tokens into n_samples chunks, calls the model with logprobs=True,
    and returns PerplexityScores for each chunk.
    """
    context = initial_context or ""
    n_samples = n_samples or len(tokens)

    sample_token_len, residue = divmod(len(tokens), n_samples)
    if n_samples == 1:
        samples = [tokens]
    else:
        samples = [
            tokens[: (i + 1) * sample_token_len] for i in range(n_samples)
        ]
        if use_residue and residue != 0:
            samples.append(tokens[-residue:])

    # Build text for each chunk
    sampless = [context + " " + " ".join(s) for s in samples]
    kwargs["logprobs"] = True

    async def _inner(api_call: APICalling):
        await api_call.invoke()
        elapsed = 0
        while (
            api_call.status not in [EventStatus.COMPLETED, EventStatus.FAILED]
            and elapsed < 5
        ):
            await asyncio.sleep(0.1)
            elapsed += 0.1
        return api_call.response

    # Create and schedule calls
    api_calls = []
    for sample_txt in sampless:
        messages = []
        if system:
            if not chat_model.sequential_exchange:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": sample_txt})
        else:
            messages.append({"role": "user", "content": sample_txt})

        api_calls.append(
            chat_model.create_api_calling(messages=messages, **kwargs)
        )

    results = await alcall(api_calls, _inner, max_concurrent=50)

    def _pplx_score(input_):
        idx, resp = input_
        return PerplexityScores(resp, samples[idx], n_samples)

    return lcall(enumerate(results), _pplx_score)


class LLMCompressor:
    """
    Compress text by selecting segments with highest perplexity tokens
    (or in practice, rank segments by logprob).
    """

    def __init__(
        self,
        chat_model: iModel,
        system=None,
        tokenizer=None,
        splitter=None,
        compression_ratio=0.2,
        n_samples=5,
        chunk_size=64,
        max_tokens_per_sample=80,
        min_pplx=0,
        split_overlap=0,
        split_threshold=0,
        verbose=True,
    ):
        # Must have "logprobs" support
        if "logprobs" not in chat_model.endpoint.acceptable_kwargs:
            raise ValueError(
                f"Model {chat_model.model_name} does not support logprobs. "
                "Please use a model that supports logprobs."
            )

        self.chat_model = chat_model
        self.tokenizer = tokenizer
        self.splitter = splitter
        self.system = system or "Concisely summarize content for storage:"
        self.compression_ratio = compression_ratio
        self.n_samples = n_samples
        self.chunk_size = chunk_size
        self.max_tokens_per_sample = max_tokens_per_sample
        self.min_pplx = min_pplx
        self.verbose = verbose
        self.split_overlap = split_overlap
        self.split_threshold = split_threshold

    def tokenize(self, text: str, **kwargs) -> list[str]:
        """
        Tokenize text. If no custom tokenizer, use the default from lionagi.
        """
        if not self.tokenizer:
            from lionagi.service.endpoints.token_calculator import (
                TokenCalculator,
            )

            return TokenCalculator.tokenize(
                text,
                encoding_name=self.chat_model.model_name,
                return_tokens=True,
            )
        if hasattr(self.tokenizer, "tokenize"):
            return self.tokenizer.tokenize(text, **kwargs)
        return self.tokenizer(text, **kwargs)

    def split(
        self,
        text: str,
        chunk_size=None,
        overlap=None,
        threshold=None,
        by_chars=False,
        return_tokens=False,
        **kwargs,
    ) -> list:
        """
        Split text into segments. If no custom splitter, default to chunk_content from lionagi.
        """
        if not self.splitter:
            from lionagi.libs.file.chunk import chunk_content

            contents = chunk_content(
                content=text,
                chunk_size=chunk_size or self.chunk_size,
                overlap=overlap or self.split_overlap,
                threshold=threshold or self.split_threshold,
                return_tokens=return_tokens,
                chunk_by="chars" if by_chars else "tokens",
            )
            return [i["chunk_content"] for i in contents]

        # If user provided an object with .split or .chunk or .segment
        for meth in ["split", "chunk", "segment"]:
            if hasattr(self.splitter, meth):
                return getattr(self.splitter, meth)(text, **kwargs)
        raise ValueError(
            "No valid method found in splitter: must have .split/.chunk/.segment"
        )

    async def rank_by_pplex(
        self,
        items: list,
        initial_text=None,
        cumulative=False,
        n_samples=None,
        use_residue=True,
        **kwargs,
    ) -> list:
        """
        Rank items (token lists or strings) by perplexity descending.
        If cumulative=True, each item is appended to the context.
        """

        async def _get_item_perplexity(item):
            # Ensure item is a list of tokens
            item_toks = item if isinstance(item, list) else [item]
            if len(item_toks) > self.max_tokens_per_sample:
                item_toks = item_toks[: self.max_tokens_per_sample]
            pplex_scores = await compute_perplexity(
                chat_model=self.chat_model,
                initial_context=initial_text,
                tokens=item_toks,
                n_samples=n_samples or self.n_samples,
                system=self.system,
                use_residue=use_residue,
                **kwargs,
            )
            # Usually we only look at pplex_scores[0], as there's one chunk
            return pplex_scores

        # If user passed a single string, tokenize it
        if isinstance(items, str):
            items = self.tokenize(items)

        if len(items) == 1:
            single_scores = await _get_item_perplexity(items[0])
            return [(items[0], single_scores[0])]

        segments = []
        if cumulative:
            ctx = initial_text or ""
            for i in items:
                seg_toks = i if isinstance(i, list) else [i]
                joined = " ".join(seg_toks)
                ctx += " " + joined
                segments.append(ctx)
        else:
            for i in items:
                seg_toks = i if isinstance(i, list) else [i]
                segments.append(" ".join(seg_toks))

        tasks = [
            asyncio.create_task(_get_item_perplexity(seg)) for seg in segments
        ]
        results = await asyncio.gather(*tasks)
        # Pair each item with the first pplex (p[0]) if multiple were returned
        pairs = [(itm, pplex[0]) for itm, pplex in zip(items, results)]

        # Sort descending by perplexity
        return sorted(pairs, key=lambda x: x[1].perplexity, reverse=True)

    async def compress(
        self,
        text: str,
        compression_ratio=None,
        initial_text=None,
        cumulative=False,
        split_kwargs=None,
        min_pplx=None,
        **kwargs,
    ) -> str:
        """
        Main method to compress text:
        1) Split text
        2) Rank by perplexity
        3) Select best segments until reaching target ratio
        """
        start = timer()
        if split_kwargs is None:
            split_kwargs = {
                "chunk_size": self.max_tokens_per_sample,
                "overlap": self.split_overlap,
                "threshold": self.split_threshold,
                "return_tokens": True,
            }

        # Tokenize once to get total length
        all_tokens = self.tokenize(text)
        original_len = len(all_tokens)
        ttl_chars = len(text)

        # Split text
        items = self.split(text, **split_kwargs)
        # items -> list of token-lists

        # Rank
        ranked = await self.rank_by_pplex(
            items=items,
            initial_text=initial_text,
            cumulative=cumulative,
            **kwargs,
        )

        # Select
        selected = self.select_by_pplex(
            ranked_items=ranked,
            target_compression_ratio=compression_ratio
            or self.compression_ratio,
            original_length=original_len,
            min_pplx=min_pplx or self.min_pplx,
        )

        # Join final
        out_str = " ".join(selected)

        if self.verbose:
            compressed_chars = len(out_str)
            ratio = compressed_chars / ttl_chars if original_len else 1
            msg = "------------------------------------------\n"
            msg += f"Compression Method: Perplexity\n"
            msg += f"Compressed Characters number: {compressed_chars}\n"
            msg += f"Character Compression Ratio: {ratio:.1%}\n"
            msg += f"Compression Time: {timer() - start:.3f}s\n"
            msg += f"Compression Model: {self.chat_model.model_name}\n"
            print(msg)

        return out_str.strip()

    def select_by_pplex(
        self,
        ranked_items: list,
        target_compression_ratio: float,
        original_length: int,
        min_pplx=0,
    ) -> list[str]:
        """
        From highest perplexity to lowest, pick items until we reach the desired ratio.
        Items below min_pplx are skipped.
        """
        desired_len = int(original_length * target_compression_ratio)

        chosen = []
        current_len = 0
        for item, info in ranked_items:
            if info.perplexity > min_pplx:
                if isinstance(item, list):
                    item_toks = to_list(item, dropna=True, flatten=True)
                else:
                    item_toks = self.tokenize(item)
                if current_len + len(item_toks) > desired_len:
                    break
                chosen.append(" ".join(item_toks))
                current_len += len(item_toks)

        return chosen


# Helper function to quickly compress text using perplexity
# (If you don't want to manually create LLMCompressor instance everywhere)
async def compress_text(
    text: str,
    chat_model: iModel,
    system: str = None,
    compression_ratio: float = 0.2,
    n_samples: int = 5,
    max_tokens_per_sample=80,
    verbose=True,
    initial_text=None,
    cumulative=False,
    split_kwargs=None,
    min_pplx=None,
    **kwargs,
) -> str:
    """
    Convenience function that instantiates LLMCompressor and compresses text.
    """
    compressor = LLMCompressor(
        chat_model=chat_model,
        system=system,
        compression_ratio=compression_ratio,
        n_samples=n_samples,
        max_tokens_per_sample=max_tokens_per_sample,
        verbose=verbose,
    )
    return await compressor.compress(
        text,
        compression_ratio=compression_ratio,
        initial_text=initial_text,
        cumulative=cumulative,
        split_kwargs=split_kwargs,
        min_pplx=min_pplx,
        **kwargs,
    )
