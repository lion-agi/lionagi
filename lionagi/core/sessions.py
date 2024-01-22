from typing import Any, Union, List, Dict, Optional
from dotenv import load_dotenv
from abc import ABC
import pandas as pd
from ..utils.nested_util import get_flattened_keys
from ..utils.call_util import rcall, lcall, alcall
from ..configs.oai_configs import oai_schema
from ..schema import DataLogger, Tool
from .._services.oai import OpenAIService
from .messages import System, Instruction, Response
from .instruction_set import InstructionSet
from .branch import Branch

load_dotenv()


class BaseSession(ABC):
    
    def __init__(self, system: Union(str, Dict)) -> None:
        self.branches = {"main": Branch(System(system))}
        self.current_branch_name = 'main'
        self.current_branch = self.branches[self.current_branch_name]

    def _new_branch(self, name: str, from_: str) -> None:
        """Creates a new branch based on an existing one.

        Args:
            name: The name of the new branch.
            from_: The name of the branch to clone from.

        Raises:
            ValueError: If the new branch name already exists or the source branch does not exist.
        """
        if name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {name}. Already existed.')
        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')

        self.branches[name] = self.branches[from_].clone()

    def switch_branch(self, name: str) -> None:
        """Switches the current active branch to the specified branch.

        Args:
            name: The name of the branch to switch to.

        Raises:
            ValueError: If the specified branch does not exist.
        """
        if name not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {name}. Not exist.')
        self.current_branch_name = name
        self.current_branch = self.branches[name]

    def merge_branch(
        self, from_: str, to_: str, update: bool = True, if_delete: bool = False
    ) -> None:
        """Merges one branch into another.

        Args:
            from_: The name of the branch to merge from.
            to_: The name of the branch to merge into.
            update: Whether to update the target branch with the source branch's data.
            if_delete: Whether to delete the source branch after merging.

        Raises:
            ValueError: If either the source or target branch name does not exist.
        """
        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')
        if to_ not in self.branches.keys():
            raise ValueError(f'Invalid target branch name {from_}. Not exist.')

        self.branches[to_].merge(self.branches[from_], update)
        if if_delete:
            if from_ == self.current_branch_name:
                self.current_branch_name = to_
                self.current_branch = self.branches[to_]
            self.branches.pop(from_)

    def delete_branch(self, name: str, verbose=True) -> bool:
        """Deletes the specified branch.

        Args:
            name: The name of the branch to delete.

        Returns:
            bool: True if the branch is deleted, False otherwise.

        Raises:
            ValueError: If the specified branch is currently active.
        """
        if name == self.current_branch_name:
            raise ValueError(f'{name} is the current active branch, please switch to another branch before delete it.')
        if name not in self.branches.keys():
            return False
        else:
            self.branches.pop(name)
            if verbose:
                print(f'Branch {name} is deleted.')
            return True
       
    #### Branch Methods: effective to current active branch 
    def change_system_message(self, system: System) -> None:
        """Changes the system message of the current active branch.

        Args:
            system: The new system message.
        """
        self.current_branch.change_system_message(system)

    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """Adds an instruction set to the current active branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to add.
        """
        self.current_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """Removes an instruction set from the current active branch.

        Args:
            name: The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.current_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """Registers one or more tools to the current active branch.

        Args:
            tools: The tool or list of tools to register.
        """
        self.current_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """Deletes a tool from the current active branch.

        Args:
            name: The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.current_branch.delete_tool(name)

    def report(self) -> Dict[str, Any]:
        """Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.current_branch.report()


class Session(BaseSession):
    """Manages a session with an AI service, handling branching, merging, and messaging.

    Attributes:
        llmconfig (Dict[str, Any]): Configuration for the language model.
        system, (Union[Dict, Any]): system message
        logger_ (DataLogger): Logger for the session data.
        service (OpenAIService): The AI service to interact with.
        branches (Dict[str, Branch]): Branches for different conversation threads.
        current_branch_name (str): The name of the active branch.
        current_branch (Branch): The active branch.
        latest_response (Response): The latest response received from the AI service.
    """
    def __init__(
        self,
        system: Union(str, System),
        dir: str = 'data/logs/',
        llmconfig: Dict[str, Any] = oai_schema["chat/completions"]["config"],
        service = OpenAIService(),
    ):
        """Initializes the session with system information, logging directory, and configuration.

        Args:
            system: System information to initialize the session with.
            dir: Directory to store session logs.
            llmconfig: Configuration for the language model.
            service: The AI service to interact with.
        """
        super().__init__(system)
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.latest_response = None
    
    
    def new_branch(self, name, from_, system=None, tools=None):
        self._new_branch(name, from_)
        if system:
            if isinstance(system, (str, dict)):
                system = System(system)
            self.branches[name].change_system_message(system)
        if tools:
            self.branches[name].register_tools(tools)
        

    async def _call_chatcompletion(self, branch: Union[str, Branch], **kwargs):
        """Calls the AI service to get a completion for the current conversation.

        Args:
            branch: Branch to run.
            **kwargs: Additional keyword arguments to pass to the AI service.

        Raises:
            NotImplementedError: If the AI service does not return a valid response.
        """
        branch = self._get_branch(branch=branch)
        messages_ = branch._to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages_, **kwargs)
        
        if "choices" in completion:
            self.logger_.add_entry({"input": str(payload), "output": str(completion)})
            self.latest_response = Response(response=completion['choices'][0])
            branch.add_message(self.latest_response)
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1

    async def chat(
        self,
        instruction: Union[Instruction, str],
        system: Optional[str] = None,
        context: Optional[Any] = None,
        name: Optional[str] = None,
        invoke: bool = True,
        out: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        branch: Union[str, Branch] = None,
        retry_kwargs = {},
        **kwargs,
    ):
        """
        Initiates a new conversation or instruction in the current branch.

        Args:
            instruction: The instruction to initiate or its content.
            system: Optional system information to update.
            context: Optional context for the instruction.
            name: Optional name of the entity sending the instruction.
            invoke: Whether to invoke tools based on the response.
            out: Whether to return the output.
            tools: Tools to be used or a flag indicating whether to use all tools.
            branch: Branch to run.
            **kwargs: Additional keyword arguments for the AI service.

        Returns:
            Any: The output of the initiation process, if requested.

        Raises:
            ValueError: If the tools argument is not in the expected format.
        """
        branch = self._get_branch(branch=branch)
        branch._handle_messages(instruction, system, context, name)
        kwargs = branch._get_tools_kwargs(tools, **kwargs)
        
        config = {**self.llmconfig, **kwargs}
        await rcall(self._call_chatcompletion(branch, **config), **retry_kwargs)
        
        return await self._output(branch, invoke, out)

    async def auto_followup(
        self,
        instruction: Union[Instruction, str]=None,
        instruction_set: InstructionSet = None,
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ):
        if not any([instruction, instruction_set]):
            raise ValueError('Either instruction or instruction_set must be provided.')
        
        if instruction_set:
            await self._instruction_set_auto_followup(
                instruction_set, num=num, branch=branch, **kwargs)
        else: 
            await self._instruction_auto_followup(
                instruction, num=num, tools=tools, branch=branch, **kwargs)

    def update_branches(self, messages, branch=None):
        if not branch:
            branch = [value for key, value in self.branches.items()]
        branch = lcall(branch, self._get_branch)
        lcall(branch, lambda x: x.merge_messages(messages))

    async def _instruction_auto_followup(
        self,
        instruction: Union[Instruction, str]=None,
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> None:
        branch = self._get_branch(branch=branch)
        if branch.tool_manager.registry != {}:
            if tools:
                kwargs = branch._tool_parser(tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.chat(
                    instruction, tool_choice="auto", tool_parsed=True, 
                    branch=branch, **kwargs)
            else:
                await self.chat(
                    instruction, tool_parsed=True, branch=branch, **kwargs)
            num -= 1
            cont_ = True if branch._tool_invoked() else False
        if num == 0:
            await self.chat(
                instruction, tool_parsed=True, branch=branch, **kwargs)

    async def _instruction_set_auto_followup(
        self,
        instruction_set: InstructionSet,
        num: Union[int, List[int]] = 3,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> None:
        """Automatically follows up an entire set of instructions.

        Args:
            instruction_set: The set of instructions to follow up.
            num: The number of follow-ups to attempt for each instruction or a list of numbers for each instruction.
            branch: Branch to run.
            **kwargs: Additional keyword arguments for the AI service.

        Raises:
            ValueError: If the number of follow-ups does not match the number of instructions.
        """
        branch = self._get_branch(branch=branch)
        if isinstance(num, List):
            if len(num) != instruction_set.instruct_len:
                raise ValueError('Unmatched auto_followup num size and instructions set size')

        current_instruct_node = instruction_set.get_instruction_by_id(instruction_set.first_instruct)
        for i in range(instruction_set.instruct_len):
            num_ = num if isinstance(num, int) else num[i]
            tools = instruction_set.get_tools(current_instruct_node)
            if tools:
                await self.auto_followup(current_instruct_node, num=num_, tools=tools, branch=branch, **kwargs)
            else:
                await self.followup(current_instruct_node, branch=branch, **kwargs)
            current_instruct_node = instruction_set.get_next_instruction(current_instruct_node)

    def _get_branch(self, branch: Union[str, Branch] = None):
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')

        return branch

    async def _output(self, branch: Union[str, Branch], invoke=True, out=True):
        """Processes the latest response and optionally invokes tools and returns output.

        Args:
            invoke: Whether to invoke tools based on the latest response.
            out: Whether to return the output.

        Returns:
            Any: The output of the latest response or tool invocation, if requested.
        """
        content_ = self.latest_response.content
        if invoke:
            try:
                tool_uses = content_
                func_calls = lcall(tool_uses["action_list"], branch.tool_manager.get_function_call)
                outs = await alcall(func_calls, branch.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    response = Response(
                        response={"function": f[0], "arguments": f[1], "output": out}
                    )
                    branch.add_message(response)
            except:
                pass
        if out:
            if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
                key = get_flattened_keys(content_)[0]
                return content_[key]
            
            return self.latest_response.content
        
    def log_to_csv(
        self, filename: str, file_exist_ok: bool = False, timestamp: bool = True,
        time_prefix: bool = False, verbose: bool = True, clear: bool = True
    ):
        self.logger_.to_csv(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp, 
            time_prefix=time_prefix, verbose=verbose, clear=clear)
        
    def log_to_jsonl(
        self, filename: str, file_exist_ok: bool = False, timestamp: bool = True,
        time_prefix: bool = False, verbose: bool = True, clear: bool = True
    ):
        self.logger_.to_jsonl(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp, 
            time_prefix=time_prefix, verbose=verbose, clear=clear)

    def messages_to_csv(self, branch = None, **kwargs):
        # kwargs of pd.DataFrame to_csv
        
        if not branch: 
            dfs = [branch.messages.copy() for key, branch in self.branches.items()]
            dfs = pd.concat(dfs).drop_duplicates()
            dfs.reset_index(drop=True, inplace=True)
            dfs.to_csv(**kwargs)
            return
        
        branch = self._get_branch(branch)
        branch.messages.to_csv(**kwargs)
        

    # async def followup(
    #     self,
    #     instruction: Union[Instruction, str],
    #     system: Optional[str] = None,
    #     context: Optional[Any] = None,
    #     out: bool = True,
    #     name: Optional[str] = None,
    #     invoke: bool = True,
    #     tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
    #     branch: Union[str, Branch] = None,
    #     **kwargs,
    # ) -> Any:
    #     """Adds a follow-up instruction to the current branch.

    #     Args:
    #         instruction: The instruction to follow up with or its content.
    #         system: Optional system information to update.
    #         context: Optional context for the instruction.
    #         out: Whether to return the output.
    #         name: Optional name of the entity sending the instruction.
    #         invoke: Whether to invoke tools based on the response.
    #         tools: Tools to be used or a flag indicating whether to use all tools.
    #         branch: Branch to run.
    #         **kwargs: Additional keyword arguments for the AI service.

    #     Returns:
    #         Any: The output of the follow-up process, if requested.

    #     Raises:
    #         ValueError: If the tools argument is not in the expected format.
    #     """
    #     return await self.chat(
    #         instruction,
    #         system=system,
    #         context=context,
    #         name=name,
    #         invoke=invoke,
    #         out=out,
    #         tools=tools,
    #         branch=branch,
    #         **kwargs,
    #     )

    # async def initiate(
    #     self,
    #     instruction: Union[Instruction, str],
    #     system: Optional[str] = None,
    #     context: Optional[Any] = None,
    #     name: Optional[str] = None,
    #     invoke: bool = True,
    #     out: bool = True,
    #     tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
    #     branch: Union[str, Branch] = None,
    #     retry_kwargs = {},
    #     **kwargs,
    # ) -> Any:        
    #     return await self.chat(
    #         instruction,
    #         system=system,
    #         context=context,
    #         name=name,
    #         invoke=invoke,
    #         out=out,
    #         tools=tools,
    #         branch=branch,
    #         retry_kwargs=retry_kwargs,
    #         **kwargs,
    #     )