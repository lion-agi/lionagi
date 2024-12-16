# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

import litellm
from dotenv import load_dotenv

litellm.drop_params = True
load_dotenv()


RESERVED_PARAMS = [
    "invoke_action",
    "instruction",
    "clear_messages",
]


class LiteiModel:

    def __init__(self, **kwargs):
        if "api_key" in kwargs:
            try:
                api_key1 = os.getenv(kwargs["api_key"], None)
                if api_key1:
                    # Store the original env var name as schema
                    self.api_key_schema = kwargs["api_key"]
                    # Store the resolved value for actual use
                    kwargs["api_key"] = api_key1
            except Exception:
                pass
        self.kwargs = kwargs
        self.acompletion = litellm.acompletion

    def to_dict(self) -> dict:
        dict_ = {
            k: v for k, v in self.kwargs.items() if k not in RESERVED_PARAMS
        }
        # If we have an api_key_schema, use that instead of the resolved value
        if hasattr(self, "api_key_schema"):
            dict_["api_key"] = self.api_key_schema
        return dict_

    @classmethod
    def from_dict(cls, data: dict) -> "LiteiModel":
        return cls(**data)

    async def invoke(self, **kwargs):
        config = {**self.kwargs, **kwargs}
        for i in RESERVED_PARAMS:
            config.pop(i, None)

        return await self.acompletion(**config)

    def __hash__(self):
        # Convert kwargs to a hashable format by serializing unhashable types
        hashable_items = []
        for k, v in self.kwargs.items():
            if isinstance(v, (list, dict)):
                # Convert unhashable types to JSON string for hashing
                v = json.dumps(v, sort_keys=True)
            elif not isinstance(v, (str, int, float, bool, type(None))):
                # Convert other unhashable types to string representation
                v = str(v)
            hashable_items.append((k, v))
        return hash(frozenset(hashable_items))

    @property
    def allowed_roles(self):
        return ["user", "assistant", "system"]
