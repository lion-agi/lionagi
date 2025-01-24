# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any

from lionagi.operatives.types import Instruct

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
    if config.get("actions"):
        if config.get("extension_allowed") and config.get("max_extensions"):
            config.pop("reason", None)
            config.pop("actions", None)
            return await branch.ReAct(**config)

        config.pop("extension_allowed", None)
        config.pop("max_extensions", None)
        return await branch.operate(**config)

    return await branch.communicate(
        **{
            k: v
            for k, v in config.items()
            if k not in Instruct.reserved_kwargs
        }
    )
