# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, Union
from uuid import uuid4

from lionagi._errors import TimeoutError
from lionagi.protocols.mail.package import PackageCategory
from lionagi.service.imodel import iModel

from .utils import AskAnalysis

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def ask(
    branch: "Branch",
    query: str,
    target: Union["Branch", iModel, str],
    *,
    timeout: int = 30,
    verbose: bool = False,
    **kwargs,
) -> Any:
    """
    Branch-level operation to send a query and await response.

    Args:
        branch: Branch initiating the ask operation
        query: Query to send
        target: Target to query (branch/model/external)
        timeout: Maximum wait time in seconds
        verbose: Whether to print progress
        **kwargs: Additional parameters for operation

    Returns:
        Response from target
    """
    # Format prompt using AskAnalysis
    prompt = AskAnalysis.format_prompt(query, target)
    ask_id = str(uuid4())

    try:
        # Handle different target types
        if isinstance(target, type(branch)):
            # Branch-to-branch
            if verbose:
                print(f"\nSending query to branch {target.id}")
            await branch.asend(
                recipient=target.id,
                category=PackageCategory.MESSAGE,
                package=prompt,
                request_source=ask_id,  # Use ask_id as request_source for tracking
            )
            raw_response = await branch.mailbox.await_response(ask_id, timeout)

        elif isinstance(target, iModel):
            # Direct model query
            if verbose:
                print("\nQuerying model directly")
            raw_response = await target.invoke(
                messages=[{"role": "user", "content": prompt}], **kwargs
            )

        else:
            # External system
            if verbose:
                print(f"\nSending query to external target: {target}")
            await branch.asend(
                recipient=str(target),
                category=PackageCategory.MESSAGE,
                package=prompt,
                request_source=ask_id,  # Use ask_id as request_source for tracking
            )
            raw_response = await branch.mailbox.await_response(ask_id, timeout)

        # Process response through AskAnalysis
        analysis = await branch.operate(
            instruction=raw_response, response_format=AskAnalysis, **kwargs
        )
        return analysis.response

    except TimeoutError:
        raise TimeoutError(f"Ask operation timed out after {timeout} seconds")

    except Exception as e:
        raise e
