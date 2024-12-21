# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import functools
from collections.abc import Callable

from pydantic import BaseModel


# Cache iscoroutinefunction results for efficiency
@functools.lru_cache(None)
def is_coro_func(f: Callable) -> bool:
    return asyncio.iscoroutinefunction(f)


class Params(BaseModel):

    def to_dict(self):
        return self.model_dump()

    def from_dict(cls, dict_: dict):
        return cls(**dict_)

    def keys(self):
        return self.model_fields.keys()
