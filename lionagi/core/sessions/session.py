from typing import Any, Union, List, Dict, Optional
from dotenv import load_dotenv
import pandas as pd
from lionagi.utils import get_flattened_keys, rcall, lcall, alcall
from lionagi.configs.oai_configs import oai_schema
from lionagi.schema import DataLogger, Tool
from lionagi._services.oai import OpenAIService
from ..messages.messages import System, Instruction, Response
from ..instruction_set.instruction_set import InstructionSet
from ..branch.branch import Branch
from .base_session import BaseSession

load_dotenv()

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
        system: Union[str, System],
        dir: str = 'data/logs/',
        llmconfig: Dict[str, Any] = oai_schema["chat/completions"]["config"],
        service = OpenAIService(),
        default_branch=None,
    ):
        """Initializes the session with system information, logging directory, and configuration.

        Args:
            system: System information to initialize the session with.
            dir: Directory to store session logs.
            llmconfig: Configuration for the language model.
            service: The AI service to interact with.
        """
        super().__init__(system, default_branch=default_branch or 'main')
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.latest_response = None
        
    
    def new_branch(self, branch_name, from_, system=None, tools=None, sys_name=None):
        self._new_branch(branch_name, from_)
        if system:
            if isinstance(system, (str, dict)):
                system = System(system, name=sys_name)
            self.branches[branch_name].change_system_message(system)
        if tools:
            self.branches[branch_name].register_tools(tools)
        

    async def _call_chatcompletion(self, branch: Union[str, Branch], **kwargs):
        """Calls the AI service to get a completion for the current conversation.

        Args:
            branch: Branch to run.
            **kwargs: Additional keyword arguments to pass to the AI service.

        Raises:
            NotImplementedError: If the AI service does not return a valid response.
        """
        branch = self.get_branch(branch=branch)
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
        branch = self.get_branch(branch=branch)
        branch._handle_messages(instruction, system, context, name)
        if tools:
            kwargs = branch._get_tools_kwargs(tools, **kwargs)
        config = {**self.llmconfig}
        if kwargs is not None:
            config = {**self.llmconfig, **kwargs}
        await self._call_chatcompletion(branch, **config)
        
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

    # update a messages df 
    def update_branches(self, messages_df, branch=None):
        if not branch:
            branch = [value for key, value in self.branches.items()]
        branch = lcall(branch, self.get_branch)
        lcall(branch, lambda x: x.merge_messages(messages_df))

    async def _instruction_auto_followup(
        self,
        instruction: Union[Instruction, str]=None,
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch: Union[str, Branch] = None,
        **kwargs,
    ) -> None:
        branch = self.get_branch(branch=branch)
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
        branch = self.get_branch(branch=branch)
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

    def get_branch(self, branch: Union[str, Branch] = None):
        if not branch:
            branch = self.current_branch
        if isinstance(branch, str):
            if branch in self.branches.keys():
                branch = self.branches[branch]
            else:
                ValueError(f'branch{branch} does not exist')

        return branch

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

    def messages_to_csv(self, branch = None, args=[], **kwargs):
        # kwargs of pd.DataFrame to_csv
        
        if not branch: 
            dfs = [branch.messages.copy() for key, branch in self.branches.items()]
            dfs = pd.concat(dfs).drop_duplicates()
            dfs.reset_index(drop=True, inplace=True)
            dfs.to_csv(*args, **kwargs)
            return
        
        branch = self.get_branch(branch)
        branch.messages.to_csv(*args, **kwargs)

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

    # def new_cluster():
    #     ...