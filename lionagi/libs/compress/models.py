# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from pydantic import BaseModel

from lionagi.operatives.models.note import Note
from lionagi.protocols.generic.log import Log


class PerplexityTokenScore(BaseModel):
    token: str
    logprob: float


class PerplexityScores(BaseModel):

    completion_response: BaseModel
    original_tokens: list[str]
    n_samples: int

    @property
    def logprobs(self) -> list[float]:
        return [i.logprob for i in self.perplexity_scores]

    @property
    def predicted_tokens(self) -> list[str]:
        return [i.token for i in self.perplexity_scores]

    @property
    def perplexity(self) -> float:
        return np.exp(np.mean(self.logprobs))

    @property
    def perplexity_scores(self) -> list[PerplexityTokenScore]:
        outs = []
        log_prob = self.completion_response.choices[0].logprobs
        n = Note.from_dict(log_prob)
        for j in range(len(n[["content"]])):
            p_ = ["content", j]
            p_token = p_ + ["token"]
            p_logprob = p_ + ["logprob"]
            p_score = PerplexityTokenScore(
                token=n[p_token], logprob=n[p_logprob]
            )
            outs.append(p_score)
        return outs

    @property
    def prompt_tokens(self) -> int:
        return self.completion_response.usage.prompt_tokens

    @property
    def completion_tokens(self) -> int:
        return self.completion_response.usage.completion_tokens

    def to_log(self) -> Log:
        dict_ = self.model_dump()
        info = dict_.pop("completion_response")
        dict_["perplexity"] = self.perplexity
        dict_["prompt_tokens"] = self.prompt_tokens
        dict_["completion_tokens"] = self.completion_tokens
        dict_["perplexity_scores"] = self.perplexity_scores

        return Log(content=dict_, info=info)
