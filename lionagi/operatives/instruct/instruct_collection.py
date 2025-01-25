# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from functools import lru_cache

from pydantic import BaseModel

from ..models.model_params import ModelParams
from .instruct import INSTRUCT_FIELD, Instruct
from .node import InstructNode

__all__ = ("InstructCollection",)


class InstructCollection(BaseModel):

    @property
    def instruct_models(self) -> list[Instruct]:
        fields = []
        for field in self.model_fields:
            if field.startswith("instruct_"):
                fields.append(field)
        return [getattr(self, field) for field in fields]

    @classmethod
    def create_model_params(
        cls, num_instructs: int = 3, **kwargs
    ) -> ModelParams:
        return create_instruct_collection_model_params(
            cls, num_instructs, **kwargs
        )

    def to_instruct_nodes(self) -> list[InstructNode]:
        return [
            InstructNode(instruct=instruct)
            for instruct in self.instruct_models
        ]


@lru_cache
def create_instruct_collection_model_params(
    base_type: type[BaseModel], num_instructs: int = 3, **kwargs
) -> ModelParams:
    model_params = ModelParams(**kwargs)
    for i in range(num_instructs):
        field = INSTRUCT_FIELD.model_copy()
        field.name = f"instruct_{i}"
        model_params.field_models.append(field)

    model_params.base_type = base_type
    return model_params
