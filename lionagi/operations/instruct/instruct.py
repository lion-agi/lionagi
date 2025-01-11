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
    """
    Determines whether to run `branch.operate()` or `branch.communicate()`
    based on the content of an `Instruct` object (e.g., if actions or
    structured response is requested).

    Args:
        branch (Branch): The branch context.
        instruct (Instruct): Contains instruction, guidance, context, etc.
        **kwargs: Additional arguments for `operate()` or `communicate()`.

    Returns:
        Any: The result from the chosen method.
    """
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
