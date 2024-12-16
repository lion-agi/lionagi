# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel


class LionIDConfig(BaseModel):
    n: int
    random_hyphen: bool
    num_hyphens: int
    hyphen_start_index: int
    hyphen_end_index: int
    prefix: str = "ln"
    postfix: str = ""