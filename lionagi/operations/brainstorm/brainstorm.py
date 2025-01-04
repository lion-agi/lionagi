# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Literal

from pydantic import BaseModel

from lionagi.operatives.instruct.instruct import (
    LIST_INSTRUCT_FIELD_MODEL,
    Instruct,
    InstructResponse,
)
from lionagi.protocols.generic.element import ID
from lionagi.session.branch import Branch
from lionagi.session.session import Session
from lionagi.utils import alcall, to_list

from ..utils import prepare_instruct, prepare_session
from .prompt import PROMPT

# ---------------------------------------------------------------------
# Data Models & Utilities
# ---------------------------------------------------------------------


class BrainstormOperation(BaseModel):
    """
    Container for the outcomes of a brainstorming session:
      1. initial: the initial result of the 'brainstorm' prompt
      2. brainstorm: the results of auto-run instructions (if auto_run = True)
      3. explore: the results of exploring those instructions (if auto_explore = True)
    """

    initial: Any
    brainstorm: list[Instruct] | None = None
    explore: list[InstructResponse] | None = None


def chunked(iterable, n):
    """
    Yield successive n-sized chunks from an iterable.

    Example:
        >>> list(chunked([1,2,3,4,5], 2))
        [[1,2],[3,4],[5]]
    """
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


# ---------------------------------------------------------------------
# Core Instruction Execution
# ---------------------------------------------------------------------


async def run_instruct(
    ins: Instruct,
    session: Session,
    branch: Branch,
    auto_run: bool,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Execute a single instruction within a brainstorming session.
    Optionally auto-run any child instructions that result.
    """

    async def _run_child_instruction(child_ins: Instruct):
        """
        Helper for recursively running child instructions.
        """
        if verbose:
            snippet = (
                child_ins.guidance[:100] + "..."
                if len(child_ins.guidance) > 100
                else child_ins.guidance
            )
            print(f"\n-----Running instruction-----\n{snippet}")
        child_branch = session.split(branch)
        return await run_instruct(
            child_ins, session, child_branch, False, verbose=verbose, **kwargs
        )

    # Prepare config for the branch operation
    config = {**ins.model_dump(), **kwargs}
    result = await branch.operate(**config)
    branch._log_manager.dump()

    # Extract any newly generated instructions
    instructs = []
    if hasattr(result, "instruct_models"):
        instructs = result.instruct_models

    # If we're allowed to auto-run child instructions, handle them
    if auto_run and instructs:
        child_results = await alcall(instructs, _run_child_instruction)
        combined = []
        for c in child_results:
            if isinstance(c, list):
                combined.extend(c)
            else:
                combined.append(c)
        combined.insert(0, result)
        return combined

    return result


async def brainstorm(
    instruct: Instruct | dict[str, Any],
    num_instruct: int = 2,
    session: Session | None = None,
    branch: Branch | ID.Ref | None = None,
    auto_run: bool = True,
    auto_explore: bool = False,
    explore_kwargs: dict[str, Any] | None = None,
    explore_strategy: Literal[
        "concurrent",
        "sequential",
        "sequential_concurrent_chunk",
        "concurrent_sequential_chunk",
    ] = "concurrent",
    branch_kwargs: dict[str, Any] | None = None,
    return_session: bool = False,
    verbose: bool = False,
    branch_as_default: bool = True,
    operative_model: type[BaseModel] | None = None,
    **kwargs: Any,
) -> Any:
    """
    High-level function to perform a brainstorming session.

    Steps:
      1. Run the initial 'instruct' prompt to generate suggestions.
      2. Optionally auto-run those suggestions (auto_run=True).
      3. Optionally explore the resulting instructions (auto_explore=True)
         using the chosen strategy (concurrent, sequential, etc.).
    """
    if operative_model:
        logging.warning(
            "The 'operative_model' parameter is deprecated and will be removed in a future version.use 'response_format' instead."
        )
        kwargs["response_format"] = kwargs.get(
            "response_format", operative_model
        )

    # -----------------------------------------------------------------
    # Basic Validations and Setup
    # -----------------------------------------------------------------
    if auto_explore and not auto_run:
        raise ValueError("auto_explore requires auto_run to be True.")

    if verbose:
        print("Starting brainstorming...")

    # Make sure the correct field model is present
    field_models: list = kwargs.get("field_models", [])
    if LIST_INSTRUCT_FIELD_MODEL not in field_models:
        field_models.append(LIST_INSTRUCT_FIELD_MODEL)
    kwargs["field_models"] = field_models

    # Prepare session, branch, and the instruction
    session, branch = prepare_session(session, branch, branch_kwargs)
    prompt_str = PROMPT.format(num_instruct=num_instruct)
    instruct = prepare_instruct(instruct, prompt_str)

    # -----------------------------------------------------------------
    # 1. Initial Brainstorm
    # -----------------------------------------------------------------
    res1 = await branch.operate(**instruct, **kwargs)
    out = BrainstormOperation(initial=res1)

    if verbose:
        print("Initial brainstorming complete.")

    # Helper to run single instructions from the 'brainstorm'
    async def run_brainstorm_instruction(ins_):
        if verbose:
            snippet = (
                ins_.guidance[:100] + "..."
                if len(ins_.guidance) > 100
                else ins_.guidance
            )
            print(f"\n-----Running instruction-----\n{snippet}")
        new_branch = session.split(branch)
        return await run_instruct(
            ins_, session, new_branch, auto_run, verbose=verbose, **kwargs
        )

    # -----------------------------------------------------------------
    # 2. Auto-run child instructions if requested
    # -----------------------------------------------------------------
    if not auto_run:
        if return_session:
            return out, session
        return out

    # We run inside the context manager for branching
    async with session.branches:
        response_ = []

        # If the initial result has instructions, run them
        if hasattr(res1, "instruct_models"):
            instructs: list[Instruct] = res1.instruct_models
            brainstorm_results = await alcall(
                instructs, run_brainstorm_instruction
            )
            brainstorm_results = to_list(
                brainstorm_results, dropna=True, flatten=True
            )

            # Filter out plain str/dict responses, keep model-based
            filtered = [
                r if not isinstance(r, (str, dict)) else None
                for r in brainstorm_results
            ]
            filtered = to_list(
                filtered, unique=True, dropna=True, flatten=True
            )

            out.brainstorm = (
                filtered if isinstance(filtered, list) else [filtered]
            )
            # Insert the initial result at index 0 for reference
            filtered.insert(0, res1)
            response_ = filtered

        # -----------------------------------------------------------------
        # 3. Explore the results (if auto_explore = True)
        # -----------------------------------------------------------------
        if response_ and auto_explore:
            # Gather all newly generated instructions
            all_explore_instructs = to_list(
                [
                    r.instruct_models
                    for r in response_
                    if hasattr(r, "instruct_models")
                ],
                dropna=True,
                unique=True,
                flatten=True,
            )

            # Decide how to explore based on the strategy
            match explore_strategy:
                # ---------------------------------------------------------
                # Strategy A: CONCURRENT
                # ---------------------------------------------------------
                case "concurrent":

                    async def explore_concurrently(ins_: Instruct):
                        if verbose:
                            snippet = (
                                ins_.guidance[:100] + "..."
                                if len(ins_.guidance) > 100
                                else ins_.guidance
                            )
                            print(f"\n-----Exploring Idea-----\n{snippet}")
                        new_branch = session.split(branch)
                        resp = await new_branch._instruct(
                            ins_, **(explore_kwargs or {})
                        )
                        return InstructResponse(instruct=ins_, response=resp)

                    res_explore = await alcall(
                        all_explore_instructs, explore_concurrently
                    )
                    out.explore = res_explore

                    # Add messages for logging / auditing
                    branch.msgs.add_message(
                        instruction="\n".join(
                            i.model_dump_json() for i in all_explore_instructs
                        )
                    )
                    branch.msgs.add_message(
                        assistant_response="\n".join(
                            i.model_dump_json() for i in res_explore
                        )
                    )

                # ---------------------------------------------------------
                # Strategy B: SEQUENTIAL
                # ---------------------------------------------------------
                case "sequential":
                    explore_results = []

                    # Warn/log if a large number of instructions
                    if len(all_explore_instructs) > 30:
                        all_explore_instructs = all_explore_instructs[:30]
                        logging.warning(
                            "Maximum number of instructions for sequential exploration is 50. defaulting to 50."
                        )
                    if len(all_explore_instructs) > 10:
                        logging.warning(
                            "Large number of instructions for sequential exploration. This may take a while."
                        )

                    for i in all_explore_instructs:
                        if verbose:
                            snippet = (
                                i.guidance[:100] + "..."
                                if len(i.guidance) > 100
                                else i.guidance
                            )
                            print(f"\n-----Exploring Idea-----\n{snippet}")
                        seq_res = await branch._instruct(
                            i, **(explore_kwargs or {})
                        )
                        explore_results.append(
                            InstructResponse(instruct=i, response=seq_res)
                        )

                    out.explore = explore_results

                # ---------------------------------------------------------
                # Strategy C: SEQUENTIAL_CONCURRENT_CHUNK
                # (chunks processed sequentially, each chunk in parallel)
                # ---------------------------------------------------------
                case "sequential_concurrent_chunk":
                    chunk_size = (explore_kwargs or {}).get("chunk_size", 5)
                    all_responses = []

                    async def explore_concurrent_chunk(
                        sub_instructs: list[Instruct], base_branch: Branch
                    ):
                        """
                        Explore instructions in a single chunk concurrently.
                        """
                        if verbose:
                            print(
                                f"\n--- Exploring a chunk of size {len(sub_instructs)} ---\n"
                            )

                        async def _explore(ins_: Instruct):
                            child_branch = session.split(base_branch)
                            child_resp = await child_branch._instruct(
                                ins_, **(explore_kwargs or {})
                            )
                            return InstructResponse(
                                instruct=ins_, response=child_resp
                            )

                        # Run all instructions in the chunk concurrently
                        res_chunk = await alcall(sub_instructs, _explore)

                        # Log messages for debugging / auditing
                        next_branch = session.split(base_branch)
                        next_branch.msgs.add_message(
                            instruction="\n".join(
                                i.model_dump_json() for i in sub_instructs
                            )
                        )
                        next_branch.msgs.add_message(
                            assistant_response="\n".join(
                                i.model_dump_json() for i in res_chunk
                            )
                        )
                        return res_chunk, next_branch

                    # Process each chunk sequentially
                    for chunk in chunked(all_explore_instructs, chunk_size):
                        chunk_result, branch = await explore_concurrent_chunk(
                            chunk, branch
                        )
                        all_responses.extend(chunk_result)

                    out.explore = all_responses

                # ---------------------------------------------------------
                # Strategy D: CONCURRENT_SEQUENTIAL_CHUNK
                # (all chunks processed concurrently, each chunk sequentially)
                # ---------------------------------------------------------
                case "concurrent_sequential_chunk":
                    chunk_size = (explore_kwargs or {}).get("chunk_size", 5)
                    all_chunks = list(
                        chunked(all_explore_instructs, chunk_size)
                    )

                    async def explore_chunk_sequentially(
                        sub_instructs: list[Instruct],
                    ):
                        """
                        Explore instructions in a single chunk, one at a time.
                        """
                        chunk_results = []
                        local_branch = session.split(branch)

                        for ins_ in sub_instructs:
                            if verbose:
                                snippet = (
                                    ins_.guidance[:100] + "..."
                                    if len(ins_.guidance) > 100
                                    else ins_.guidance
                                )
                                print(
                                    f"\n-----Exploring Idea (sequential in chunk)-----\n{snippet}"
                                )

                            seq_resp = await local_branch._instruct(
                                ins_, **(explore_kwargs or {})
                            )
                            chunk_results.append(
                                InstructResponse(
                                    instruct=ins_, response=seq_resp
                                )
                            )

                        return chunk_results

                    # Run all chunks in parallel
                    all_responses = await alcall(
                        all_chunks,
                        explore_chunk_sequentially,
                        flatten=True,
                        dropna=True,
                    )
                    out.explore = all_responses

                    # Log final messages
                    branch.msgs.add_message(
                        instruction="\n".join(
                            i.model_dump_json() for i in all_explore_instructs
                        )
                    )
                    branch.msgs.add_message(
                        assistant_response="\n".join(
                            i.model_dump_json() for i in all_responses
                        )
                    )

    if branch_as_default:
        session.change_default_branch(branch)

    # -----------------------------------------------------------------
    # 4. Return Results
    # -----------------------------------------------------------------
    if return_session:
        return out, session
    return out
