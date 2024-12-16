# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field


class Option(BaseModel):
    mirostat: int = Field(
        0, description="Enable Mirostat sampling for controlling perplexity."
    )

    mirostat_eta: float = Field(
        0.1,
        description="Influences how quickly the algorithm responds to feedback from the generated text. ",
    )

    mirostat_tau: float = Field(
        5.0,
        description="Controls the balance between coherence and diversity of the output.",
    )

    num_ctx: int = Field(
        2048,
        description="Sets the size of the context window used to generate the next token.",
    )

    repeat_last_n: int = Field(
        64,
        description="Sets how far back for the model to look back to prevent repetition.",
    )

    repeat_penalty: float = Field(
        1.1, description="Sets how strongly to penalize repetitions."
    )

    temperature: float = Field(
        0.8, description="The temperature of the model."
    )

    seed: int = Field(
        0, description="Sets the random number seed to use for generation."
    )

    stop: str = Field(None, description="Sets the stop sequences to use.")

    tfs_z: float = Field(
        1,
        description="Tail free sampling is used to reduce the impact of less probable tokens from the output.",
    )

    num_predict: int = Field(
        128,
        description="Maximum number of tokens to predict when generating text.",
    )

    top_k: int = Field(
        40, description="Reduces the probability of generating nonsense."
    )

    top_p: float = Field(0.9, description="Works together with top-k.")

    min_p: float = Field(
        0.0,
        description="Alternative to the top_p, and aims to ensure a balance of quality and variety. "
        "The parameter p represents the minimum probability for a token to be considered, "
        "relative to the probability of the most likely token. ",
    )
