from typing import Any, Dict, List, Optional, Union
from pandas import DataFrame

from lionagi.core.schema import BaseActionNode, DataLogger
from lionagi.core.action import ActionManager
from lionagi.core.session.base.schema import System, Instruction
from lionagi.core.session.branch import Branch
from lionagi.core.session.base.base_session import BaseSession

class Session(BaseSession):

    def __init__(
            self,
            system: System | str | Dict[str, Any] | None = None,
            default_branch_name: str | None = None,
            sender: str | None = None,
            llmconfig: Dict | None = None,
            service: Any = None,
            branches: Dict[str, Branch] | None = None,
            actions: BaseActionNode | List[BaseActionNode] | None = None,
            instruction_sets: Dict | None = None,
            action_manager: ActionManager | None = None,
            messages: DataFrame | None = None,
            datalogger: DataLogger | None = None,
            persist_path: str | None = None,
            **kwargs: Any
    ):
        super().__int__(
            system=system,
            default_branch_name=default_branch_name,
            sender=sender,
            llmconfig=llmconfig,
            service=service,
            branches=branches,
            actions=actions,
            instruction_sets=instruction_sets,
            action_manager=action_manager,
            messages=messages,
            datalogger=datalogger,
            persist_path=persist_path,
            **kwargs
        )

    async def chat(self, instruction: Union[Instruction, str],
                   context: Optional[Any] = None,
                   sender: Optional[str] = None,
                   system: Optional[Union[System, str, Dict[str, Any]]] = None,
                   actions: Union[bool, BaseActionNode, List[BaseActionNode], str, List[
                       str]] = False,
                   out: bool = True, invoke: bool = True, branch: Branch | str = None,
                   **kwargs) -> Any:
        branch = self.get_branch(branch)

        return await branch.chat(
            instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(self, instruction: Union[Instruction, str],
                    context: Optional[Any] = None,
                    sender: Optional[str] = None,
                    system: Optional[Union[System, str, Dict[str, Any]]] = None,
                    actions: Union[bool, BaseActionNode, List[BaseActionNode], str,
                    List[str]] = True,
                    num_rounds: int = 1, branch=None, **kwargs) -> Any:
        branch = self.get_branch(branch)

        return await branch.ReAct(
            instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            persist_path: Union[
                bool, BaseActionNode, List[BaseActionNode], str, List[str], List[
                    Dict]] = False,
            max_followup: int = 3,
            out=True,
            branch=None,
            **kwargs
    ) -> Any:
        branch = self.get_branch(branch)

        return await branch.auto_followup(
            instruction=instruction, context=context,
            sender=sender, system=system, persist_path=persist_path,
            max_followup=max_followup, out=out, **kwargs
        )

