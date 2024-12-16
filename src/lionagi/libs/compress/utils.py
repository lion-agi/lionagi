"""
Copyright 2024 HaiyangLi

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import asyncio

from lionagi.integrations.litellm_.imodel import iModel

from .models import PerplexityScores


async def compute_perplexity(
    imodel: iModel,
    initial_context: str = None,
    tokens: list[str] = None,
    system_msg: str = None,
    n_samples: int = 1,  # number of samples used for the computation
    use_residue: bool = True,  # whether to use residue for the last sample
    **kwargs,
) -> list[PerplexityScores]:
    tasks = []
    context = initial_context or ""

    n_samples = n_samples or len(tokens)
    sample_token_len, residue = divmod(len(tokens), n_samples)
    samples = []

    if n_samples == 1:
        samples = [tokens]
    else:
        samples = [
            tokens[: (i + 1) * sample_token_len] for i in range(n_samples)
        ]

        if use_residue and residue != 0:
            samples.append(tokens[-residue:])

    sampless = [context + " ".join(sample) for sample in samples]

    for sample in sampless:
        messages = (
            [{"role": "system", "content": system_msg}] if system_msg else []
        )
        messages.append(
            {"role": "user", "content": sample},
        )
        task = asyncio.create_task(
            imodel.invoke(
                messages=messages,
                logprobs=True,
                max_tokens=sample_token_len,
                **kwargs,
            )
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    outs = []

    for idx, item in enumerate(results):
        p = PerplexityScores(
            completion_response=item,
            original_tokens=samples[idx],
            n_samples=n_samples,
        )
        outs.append(p)

    return outs
