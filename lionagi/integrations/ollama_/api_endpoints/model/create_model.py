# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from pydantic import Field

from ..data_models import OllamaEndpointRequestBody, OllamaEndpointResponseBody


class OllamaCreateModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(description="name of the model to create")

    modelfile: str | None = Field(
        None, description="Contents of the Modelfile"
    )

    stream: bool | None = Field(
        True,
        description="if 'false' the response will be returned as a single response object, "
        "rather than a stream of objects",
    )

    path: str | None = Field(None, description="path to the Modelfile")


class OllamaCreateModelResponseBody(OllamaEndpointResponseBody):
    status: str = Field(None)
