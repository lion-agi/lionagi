from lionagi.core.session.branch import Branch
from lionagi.core.session.session import Session
from lionagi.protocols.operatives.instruct import Instruct


def prepare_session(
    session=None, branch=None, branch_kwargs=None
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


def prepare_instruct(instruct: Instruct | dict, prompt: str):
    if isinstance(instruct, Instruct):
        instruct = instruct.to_dict()
    if not isinstance(instruct, dict):
        raise ValueError(
            "instruct needs to be an InstructModel object or a dictionary of valid parameters"
        )

    guidance = instruct.get("guidance", "")
    instruct["guidance"] = f"\n{prompt}\n{guidance}"
    return instruct