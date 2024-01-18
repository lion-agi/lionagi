import json
from typing import Any, Union, List, Dict, Union, Optional
from dotenv import load_dotenv

from ..configs.oai_configs import oai_schema
from ..utils.nested_util import get_flattened_keys
from ..utils.call_util import lcall, alcall
from ..schema import DataLogger, Tool
from .._services.oai import OpenAIService
from .messages import System, Instruction, Response
from .instruction_set import InstructionSet
from .branch import Branch


load_dotenv()
OAIService = OpenAIService()

class Session:
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
        system: str,
        dir: str = None,
        llmconfig: Dict[str, Any] = oai_schema["chat/completions"]["config"],
        service: OpenAIService = OAIService,
    ):
        """Initializes the session with system information, logging directory, and configuration.

        Args:
            system: System information to initialize the session with.
            dir: Directory to store session logs.
            llmconfig: Configuration for the language model.
            service: The AI service to interact with.
        """
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.branches = {"main": Branch(System(system))}
        self.current_branch_name = 'main'
        self.current_branch = self.branches[self.current_branch_name]
        self.latest_response = None

    def new_branch(self, name: str, from_: str) -> None:
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

    async def call_chatcompletion(self, branch: Union[str, Branch], **kwargs):
        """Calls the AI service to get a completion for the current conversation.

        Args:
            branch: Branch to run.
            **kwargs: Additional keyword arguments to pass to the AI service.

        Raises:
            NotImplementedError: If the AI service does not return a valid response.
        """

        messages = branch.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self.logger_({"input": payload, "output": completion})
            self.latest_response = Response(response=completion['choices'][0])
            branch.add_message(self.latest_response)
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1

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
                    response = Response(response={"function": f[0], "arguments": f[1], "output": out})
                    branch.add_message(response)
            except:
                pass
        if out:
            if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
                key = get_flattened_keys(content_)[0]
                return content_[key]
            
            return self.latest_response.content

    def _tool_parser(self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]],
                     branch: Union[str, Branch], **kwargs) -> Dict:
        """Parses tools and returns keyword arguments for tool usage.

        Args:
            tools: A single tool, a list of tools, or a tool name.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict: Keyword arguments including tool schemas.

        Raises:
            ValueError: If the tool is not registered.
        """
        # 1. single schema: dict
        # 2. tool: Tool
        # 3. name: str
        # 4. list: 3 types of lists
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if branch.tool_manager.name_existed(tool):
                    tool = branch.tool_manager.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": branch.tool_manager.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}

        return kwargs

    def _is_invoked(self, branch: Union[str, Branch]):
        """Checks if the latest message in the current branch has invoked a tool.

        Returns:
            bool: True if a tool has been invoked, False otherwise.
        """
        content = branch.messages.iloc[-1]['content']
        try:
            if json.loads(content)['action_response'].keys() >= {'function', 'arguments', 'output'}:
                return True
        except:
            return False

    async def initiate(
        self,
        instruction: Union[Instruction, str],
        system: Optional[str] = None,
        context: Optional[Any] = None,
        name: Optional[str] = None,
        invoke: bool = True,
        out: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> Any:
        """Initiates a new conversation or instruction in the current branch.

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
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')
        if system:
            branch.change_system_message(System(system))
        if isinstance(instruction, Instruction):
            branch.add_message(instruction)
        else:
            instruct = Instruction(instruction, context, name)
            branch.add_message(instruct)
        if branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(tools=tools, branch=branch, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(branch=branch, **config)

        return await self._output(branch, invoke, out)

    async def followup(
        self,
        instruction: Union[Instruction, str],
        system: Optional[str] = None,
        context: Optional[Any] = None,
        out: bool = True,
        name: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> Any:
        """Adds a follow-up instruction to the current branch.

        Args:
            instruction: The instruction to follow up with or its content.
            system: Optional system information to update.
            context: Optional context for the instruction.
            out: Whether to return the output.
            name: Optional name of the entity sending the instruction.
            invoke: Whether to invoke tools based on the response.
            tools: Tools to be used or a flag indicating whether to use all tools.
            branch: Branch to run.
            **kwargs: Additional keyword arguments for the AI service.

        Returns:
            Any: The output of the follow-up process, if requested.

        Raises:
            ValueError: If the tools argument is not in the expected format.
        """
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')
        if system:
            branch.change_system_message(System(system))
        if isinstance(instruction, Instruction):
            branch.add_message(instruction)
        else:
            instruct = Instruction(instruction, context, name)
            branch.add_message(instruct)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if branch.tool_manager.registry != {}:
                if tools:
                    kwargs = self._tool_parser(tools=tools, branch=branch, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(branch=branch, **config)

        return await self._output(branch, invoke, out)

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> None:
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')
        if branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(tools=tools, branch=branch, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.followup(instruction, tool_choice="auto", tool_parsed=True, branch=branch, **kwargs)
            else:
                await self.followup(instruction, tool_parsed=True, branch=branch, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked(branch) else False
        if num == 0:
            await self.followup(instruction, tool_parsed=True, branch=branch, **kwargs)

    async def instruction_set_auto_followup(
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
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')
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
