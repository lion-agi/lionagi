# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..typing._pydantic import BaseModel
from ..typing._typing import UNDEFINED, Any, Self

__all__ = ("BaseAutoModel",)


class BaseAutoModel(BaseModel):
    """a hashable pydantic model interface with to_dict and from_dict method"""

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """kwargs for pydantic model_dump()"""
        return {
            k: v
            for k, v in self.model_dump(**kwargs).items()
            if v is not UNDEFINED
        }

    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> Self:
        """kwargs for model_validate"""
        return cls.model_validate(data, **kwargs)

    def __hash__(self) -> int:
        return hash(str(self.to_dict()))
