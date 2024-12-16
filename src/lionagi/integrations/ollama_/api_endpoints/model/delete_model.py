# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody


class OllamaDeleteModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(description="Name of the model to delete")
