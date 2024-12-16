# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict


class OllamaEndpointRequestBody(BaseModel):
    model_config = ConfigDict(
        extra="forbid", use_enum_values=True, validate_assignment=True
    )


class OllamaEndpointResponseBody(BaseModel):
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)
