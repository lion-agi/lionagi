from typing import Any, List, Union, Dict, Optional
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool
from lionagi.utils import as_dict, lcall, get_flattened_keys, alcall
from lionagi.configs.oai_configs import oai_schema
from lionagi._services.oai import OpenAIService
from ..messages.messages import System, Instruction
from ..instruction_set.instruction_set import InstructionSet
from ..branch.branch import Branch

            
load_dotenv()
OAIService = OpenAIService()

class Session:
    """
    Represents a session with conversation branches, tool management, and logging.

    This class encapsulates the management of different conversation branches, each with its own
    messages, instruction sets, and tools. It also handles logging and interactions with an external service.

    Attributes:
        branches (Dict): A dictionary of conversation branches.
        default_branch (Branch): The default branch for the session.
        default_branch_name (str): The name of the default branch.
        llmconfig (Dict[str, Any]): Configuration settings for the language model.
        logger_ (DataLogger): Logger for session data.
        service: Service used for handling chat completions and other operations.
    """
    def __init__(
        self,
        system: Union[str, System],
        dir: str = None,
        llmconfig: Dict[str, Any] = None,
        service  = OAIService,
        branches = None,
        default_branch=None,
        default_branch_name='main',
    ):
        """
        Initialize a Session object.

        Args:
            system (Union[str, System]): Initial system message or System object for the default branch.
            dir (str, optional): Directory path for storing logs.
            llmconfig (Dict[str, Any], optional): Configuration settings for the language model.
            service (OAIService, optional): Service used for handling chat completions and other operations.
            branches (optional): Pre-existing branches to initialize in the session.
            default_branch (optional): Default branch for the session.
            default_branch_name (str, optional): Name of the default branch, defaults to 'main'.
        """

        self.branches = branches or {}
        self.default_branch = default_branch or Branch()
        self.default_branch.add_message(system=system)
        self.default_branch_name = default_branch_name
        self.branches.update({self.default_branch_name: self.default_branch})
        self.llmconfig = llmconfig or oai_schema["chat/completions"]["config"]
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        
    def new_branch(
        self, 
        branch_name: str, 
        system: Union[str, System]=None, 
        tools=None, 
        sender=None, 
    ) -> None:
        """
        Create a new branch in the session.

        Args:
            branch_name (str): Name of the new branch.
            system (Union[str, System], optional): Initial system message or System object for the new branch.
            tools (optional): Tools to register with the new branch.
            sender (optional): Sender of the initial system message.

        Raises:
            ValueError: If the branch name already exists in the session.
        """
        new_ = Branch()
        
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Already existed.')
        if system:
            new_.change_system_message(system, sender=sender)
        if tools:
            new_.register_tools(tools)
            
        self.branches[branch_name] = new_

    def get_branch(self, branch: Union[Branch, str]=None, get_name=False):
        """
        Retrieve a branch from the session.

        Args:
            branch (Union[Branch, str], optional): The branch or its name to retrieve.
                                                   Defaults to the default branch if not specified.
            get_name (bool, optional): If True, returns the name of the branch along with the branch object.

        Returns:
            Union[Branch, Tuple[Branch, str]]: The branch object or a tuple of the branch object and its name.

        Raises:
            ValueError: If the branch does not exist in the session.
        """
        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f'Invalid branch name {branch}. Not exist.')
            else:
                if get_name: 
                    return self.branches[branch], branch
                return self.branches[branch]
        
        elif isinstance(branch, Branch) and branch in self.branches.values():
            if get_name:
                return branch, [key for key, value in self.branches.items() if value == branch][0]
            return branch

        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch
        
        else:
            raise ValueError(f'Invalid branch input {branch}.')

    def change_default(self, branch: Union[str, Branch]) -> None:
        """
        Change the default branch of the session.

        Args:
            branch (Union[str, Branch]): The branch or its name to set as the new default.
        """
        branch_, name_ = self.get_branch(branch, get_name=True)
        self.default_branch = branch_
        self.default_branch_name = name_

    def delete_branch(self, branch: Union[Branch, str], verbose=True) -> bool:
        """
        Delete a branch from the session.

        Args:
            branch (Union[Branch, str]): The branch or its name to delete.
            verbose (bool, optional): If True, prints a message upon successful deletion.

        Returns:
            bool: True if the branch was deleted, False otherwise.

        Raises:
            ValueError: If attempting to delete the current active default branch.
        """
        branch, branch_name = self.get_branch(branch, get_name=True)
        if branch_name == self.default_branch_name:
            raise ValueError(f'{branch_name} is the current active branch, please switch to another branch before delete it.')

        else:
            self.branches.pop(branch_name)
            if verbose:
                print(f'Branch {branch_name} is deleted.')
            return True

    def merge_branch(
        self, 
        from_: Union[str, Branch], 
        to_: Union[str, Branch], 
        update: bool = True, 
        if_delete: bool = False
    ) -> None:
        """
        Merge one branch into another within the session.

        Args:
            from_ (Union[str, Branch]): The branch or its name to merge from.
            to_ (Union[str, Branch]): The branch or its name to merge into.
            update (bool, optional): If True, updates existing elements; keeps only new ones otherwise.
            if_delete (bool, optional): If True, deletes the 'from' branch after merging.

        Raises:
            ValueError: If the branch does not exist in the session.
        """
        from_ = self.get_branch(branch=from_)
        to_, to_name = self.get_branch(branch=to_)
        to_.merge(from_, update=update)
        
        if if_delete:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_
            self.delete_branch(from_, verbose=False)

    async def call_chatcompletion(self, branch_: Branch = None, **kwargs):
        """
        Call the chat completion service for a given branch.

        Args:
            branch_ (Branch, optional): The branch to use for the chat completion call.
            **kwargs: Additional keyword arguments to pass to the service.

        This method interacts with the configured service to process chat completions and updates the branch.
        """
        messages = branch_.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self.logger_.add_entry({"input": payload, "output": completion})
            branch_.add_message(response=completion['choices'][0])
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1

    async def _output(self, branch_: Branch, invoke=True, out=True):
        """
        Process and return the output from the latest message in a branch.

        Args:
            branch_ (Branch): The branch to process.
            invoke (bool, optional): If True, invokes any actionable responses.
            out (bool, optional): If True, returns the content of the latest message.

        Returns:
            Any: The output content from the latest message in the branch.
        """
        content_ = as_dict(branch_.messages.content.iloc[-1])
        if invoke:
            try:
                tool_uses = content_
                func_calls = lcall(
                    [as_dict(i) for i in tool_uses["action_list"]], 
                    branch_.tool_manager.get_function_call
                )
                outs = await alcall(func_calls, branch_.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    branch_.add_message(response={"function": f[0], "arguments": f[1], "output": out})
            except:
                pass
        if out:
            if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
                key = get_flattened_keys(content_)[0]
                return content_[key]
            
            return content_

    def _tool_parser(self, branch_: Branch, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        """
        Parse tools for a given branch.

        Args:
            branch_ (Branch): The branch to parse tools for.
            tools (Union[Dict, Tool, List[Tool], str, List[str], List[Dict]]): The tools to parse.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict: Parsed tools in a dictionary format.

        Raises:
            ValueError: If a specified tool is not registered in the branch's tool manager.
        """
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if branch_.tool_manager.name_existed(tool):
                    tool = branch_.tool_manager.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": branch_.tool_manager.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}

        return kwargs

    async def chat(
        self,
        instruction: Union[Instruction, str],
        system: Optional[str] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        branch = None,
        **kwargs,
    ) -> Any:
        """
        Conduct a chat session using the specified instruction and branch.

        Args:
            instruction (Union[Instruction, str]): The instruction for the chat session.
            system (Optional[str], optional): System message to use for the session.
            context (Optional[Any], optional): Contextual information for the session.
            out (bool, optional): If True, outputs the response from the chat session.
            sender (Optional[str], optional): The sender of the instruction.
            invoke (bool, optional): If True, invokes any actionable responses.
            tools (Union[bool, Tool, List[Tool], str, List[str]], optional): Tools to use in the session.
            branch (optional): The branch to use for the session.
            **kwargs: Additional keyword arguments for configuration.

        Returns:
            Any: The result of the chat session, typically the response content.
        """
        branch = self.get_branch(branch=branch)
        if system:
            branch.change_system_message(system)
        branch.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if branch.tool_manager.registry != {}:
                if tools:
                    kwargs = self._tool_parser(branch_=branch, tools=tools, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(branch_=branch, **config)

        return await self._output(branch_=branch, invoke=invoke, out=out)

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch=None,
        **kwargs,
    ) -> None:
        """
        Automatically follow up on a chat session with additional instructions.

        Args:
            instruction (Union[Instruction, str]): The initial instruction for the follow-up.
            num (int, optional): Number of follow-up iterations.
            tools (Union[bool, Tool, List[Tool], str, List[str], List[Dict]], optional): Tools to use for the follow-ups.
            branch (optional): The branch to use for the follow-ups.
            **kwargs: Additional keyword arguments for configuration.

        This method facilitates automatic follow-ups in a chat session based on the provided instruction.
        """

        branch = self.get_branch(branch)
        if branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(branch_=branch, tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.chat(instruction, tool_choice="auto", tool_parsed=True, branch=branch, **kwargs)
            else:
                await self.chat(instruction, tool_parsed=True, branch=branch, **kwargs)
            num -= 1
            cont_ = True if branch._is_invoked() else False
        if num == 0:
            await self.chat(instruction, tool_parsed=True, branch=branch, **kwargs)

    async def instruction_set_auto_followup(
        self,
        instruction_set: InstructionSet,
        num: Union[int, List[int]] = 3,
        branch=None,
        **kwargs,
    ) -> None:
        """
        Automatically follows up an entire set of instructions.

        Args:
            instruction_set: The set of instructions to follow up.
            num: The number of follow-ups to attempt for each instruction or a list of numbers for each instruction.
            **kwargs: Additional keyword arguments for the AI service.

        Raises:
            ValueError: If the number of follow-ups does not match the number of instructions.
        """
        branch = self.get_branch(branch)
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
                await self.chat(current_instruct_node, branch=branch)
            current_instruct_node = instruction_set.get_next_instruction(current_instruct_node)

#### Branch Methods: effective to default branch
    def change_system_message(self, system: System) -> None:
        """Changes the system message of the current active branch.

        Args:
            system: The new system message.
        """
        self.default_branch.change_system_message(system)

    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """Adds an instruction set to the current active branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to add.
        """
        self.default_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """Removes an instruction set from the current active branch.

        Args:
            name: The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.default_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """Registers one or more tools to the current active branch.

        Args:
            tools: The tool or list of tools to register.
        """
        self.default_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """Deletes a tool from the current active branch.

        Args:
            name: The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.default_branch.delete_tool(name)

    def describe(self) -> Dict[str, Any]:
        """Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.default_branch.describe()
