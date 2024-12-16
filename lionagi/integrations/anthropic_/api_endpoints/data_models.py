# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict


class AnthropicEndpointRequestBody(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class AnthropicEndpointResponseBody(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class AnthropicEndpointQueryParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class AnthropicEndpointPathParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )
