# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols.base import ID
from lionagi.session.types import Branch, Session

from ..fields.instruct import Instruct


def prepare_session(
    session: Session = None,
    branch: ID[Branch].Ref = None,
    branch_kwargs: dict = None,
) -> tuple[Session, Branch]:
    if session is not None:
        if branch is not None:
            branch: Branch = session.branches[branch]
        else:
            branch = session.new_branch(**(branch_kwargs or {}))
    else:
        session = Session()
        if isinstance(branch, Branch):
            session.branches.include(branch)
            session.default_branch = branch
        if branch is None:
            branch = session.new_branch(**(branch_kwargs or {}))

    return session, branch


def prepare_instruct(instruct: Instruct | dict, prompt: str) -> dict:
    if isinstance(instruct, Instruct):
        instruct = instruct.to_dict()
    if not isinstance(instruct, dict):
        raise ValueError(
            "instruct needs to be an InstructModel object or a dictionary of valid parameters"
        )

    guidance = instruct.get("guidance", "")
    instruct["guidance"] = f"\n{prompt}\n{guidance}"
    return instruct
