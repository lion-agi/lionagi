# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from .endpoint import EndPoint


def match_endpoint(
    provider: str,
    base_url: str,
    endpoint: str,
    endpoint_params: list[str] | None = None,
) -> EndPoint: ...
