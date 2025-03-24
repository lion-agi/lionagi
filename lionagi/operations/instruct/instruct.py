# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any

from lionagi.fields.instruct import Instruct

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def instruct(
    branch: "Branch",
    instruct: Instruct,
    /,
    **kwargs,
) -> Any:
    config = {
        **(instruct.to_dict() if isinstance(instruct, Instruct) else instruct),
        **kwargs,
    }
    if any(i in config and config[i] for i in Instruct.reserved_kwargs):
        if "response_format" in config or "request_model" in config:
            return await branch.operate(**config)
        for i in Instruct.reserved_kwargs:
            config.pop(i, None)

    return await branch.communicate(**config)
