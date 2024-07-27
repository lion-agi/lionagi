import asyncio
import numpy as np
from typing import Callable
from lion_core.libs import to_list, nget
from lionagi.os.operator.imodel.imodel import iModel


async def compute_perplexity(
    imodel: iModel,
    initial_context: str = None,
    tokens: list[str] = None,
    system_msg: str = None,
    n_samples: int = 1,  # number of samples used for the computation
    use_residue: bool = True,  # whether to use residue for the last sample
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

        if use_residue and residue != 0:
            samples.append(tokens[-residue:])

    sampless = [context + " ".join(sample) for sample in samples]

    for sample in sampless:
        messages = [{"role": "system", "content": system_msg}] if system_msg else []
        messages.append(
            {"role": "user", "content": sample},
        )

        task = asyncio.create_task(
            imodel.chat_completion(
                messages=messages,
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

    logprobs = to_list([[i[1] for i in d["logprobs"]] for d in results_], flatten=True)

    return {
        "tokens": tokens,
        "n_samples": n_samples,
        "num_prompt_tokens": num_prompt_tokens,
        "num_completion_tokens": num_completion_tokens,
        "logprobs": logprobs,
        "perplexity": np.exp(np.mean(logprobs)),
    }


def select_by_pplex(
    ranked_items: list,
    target_compression_ratio: float,
    original_length: int,
    tokenizer: Callable,
    min_pplex: float,
):
    min_pplex = min_pplex or 0

    desired_length = int(original_length * target_compression_ratio)
    items = []
    current_length = 0

    for item, info in ranked_items:
        if info["perplexity"] > min_pplex:
            item = tokenizer(item) if isinstance(item, str) else item
            item = item if isinstance(item, list) else [item]
            item = to_list(item, dropna=True, flatten=True)
            if current_length + len(item) > desired_length:
                break
            else:
                current_length += len(item)
                items.append("".join(item))

    return items
