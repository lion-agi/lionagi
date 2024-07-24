from __future__ import annotations
from abc import ABC
from lion_core.abc import BaseiModel
from lion_core.libs import nget, to_str
from lion_core.exceptions import LionResourceError, LionTypeError
from lion_core.generic.note import Note
from lion_core.generic.component import Component
from .imodel import iModel
import asyncio
import numpy as np
from lion_core.libs import to_list, nget


class iModelExtension(ABC):

    @staticmethod
    async def compute_perplexity(
        imodel: iModel,
        /,
        initial_context: str = None,
        tokens: list[str] = None,
        system_msg: str = None,
        n_samples: int = 1,  # number of samples used for the computation
        use_residual: bool = True,  # whether to use residue for the last sample
        **kwargs,  # additional arguments for the model
    ) -> tuple[list[str], float]:
        tasks = []
        context = initial_context or ""

        n_samples = n_samples or len(tokens)
        sample_token_len, residue = divmod(len(tokens), n_samples)
        samples = []

        if n_samples == 1:
            samples = [tokens]
        else:
            samples = [tokens[: (i + 1) * sample_token_len] for i in range(n_samples)]

            if use_residual and residue != 0:
                samples.append(tokens[-residue:])

        sampless = [context + " ".join(sample) for sample in samples]

        for sample in sampless:
            messages = [{"role": "system", "content": system_msg}] if system_msg else []
            messages.append(
                {"role": "user", "content": sample},
            )

            task = asyncio.create_task(
                await imodel.call(
                    input_=messages,
                    endpoint="chat/completions",
                    logprobs=True,
                    max_tokens=sample_token_len,
                    **kwargs,
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)  # result is (payload, response)
        results_ = []
        num_prompt_tokens = 0
        num_completion_tokens = 0

        for idx, result in enumerate(results):
            _dict = {}
            _dict["tokens"] = samples[idx]

            num_prompt_tokens += nget([1, "usage", "prompt_tokens"], result, 0)
            num_completion_tokens += nget([1, "usage", "completion_tokens"], result, 0)
            logprobs = nget([1, "choices", 0, "logprobs", "content"], result, [])
            logprobs = to_list(logprobs, flatten=True, dropna=True)
            _dict["logprobs"] = [(i["token"], i["logprob"]) for i in logprobs]
            results_.append(_dict)

        logprobs = to_list(
            [[i[1] for i in d["logprobs"]] for d in results_], flatten=True
        )

        return {
            "tokens": tokens,
            "n_samples": n_samples,
            "num_prompt_tokens": num_prompt_tokens,
            "num_completion_tokens": num_completion_tokens,
            "logprobs": logprobs,
            "perplexity": np.exp(np.mean(logprobs)),
        }

    @staticmethod
    async def embed_node(
        imodel: iModel, /, node: Component, field="content", **kwargs
    ) -> bool:
        """
        if not specify field, we embed node.content
        """
        if not isinstance(node, Component):
            raise LionTypeError("node must be a Component or its subclass object")

        embed_str = getattr(node, field)

        if isinstance(embed_str, Note):
            embed_str = embed_str.to_dict()
        if isinstance(embed_str, dict) and "images" in embed_str:
            embed_str.pop("images", None)
            embed_str.pop("image_detail", None)

        embed_str = to_str(embed_str)
        num_tokens = imodel.service.provider.token_calculator.calculate(
            "embeddings", embed_str
        )
        model = imodel.service.endpoints["embeddings"].endpoint_config["model"]

        # model specs should be a note object
        token_limit = imodel.service.provider.model_specs[model].token_limit

        if token_limit and num_tokens > token_limit:
            raise LionResourceError(
                f"Number of tokens {num_tokens} exceeds the limit {token_limit}"
            )

        payload, embed = await imodel.embed(embed_str, **kwargs)
        payload.pop("input")
        node.embedding = nget(["data", 0, "embedding"], embed, None)
        node.metadata.set("embedding_meta", payload)
