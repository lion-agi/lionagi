import json
import pandas as pd
from typing import Any, Optional, Union, List, Dict, Type
from dotenv import load_dotenv
from lionagi.configs.oai_configs import oai_schema
from lionagi.utils import lcall, alcall
from lionagi.schema import DataLogger, Tool
from lionagi.endpoints import ChatCompletion
from lionagi.services import OpenAIService
from lionagi.tools.tool_manager import ToolManager
from .messages import Message, Instruction, Response
from .conversation import Conversation








load_dotenv()
OAIService = OpenAIService()

class Session:

    def __init__(
        self, system, dir=None, llmconfig=oai_schema['chat']['config'], 
        service=OAIService
    ):
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.tool_manager = ToolManager()
        self.branches = {"main": self.conversation}
    
    def set_dir(self, dir):
        self.logger_.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        self.service = service
    
    async def _output(self, invoke=True, out=True):
        if invoke:
            try: 
                tool_uses = json.loads(self.conversation.responses[-1].msg_content)
                if 'function_list' in tool_uses.keys():
                    func_calls = lcall(tool_uses['function_list'], self.tool_manager.get_function_call)
                else:
                    func_calls = lcall(tool_uses['tool_uses'], self.tool_manager.get_function_call)

                outs = await alcall(func_calls, self.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    response = {"function": f[0], "arguments": f[1], "output": out}
                    self.conversation.add_messages(response=response)
            except:
                pass
        if out:
            return self.conversation.responses[-1].msg_content
    
    def _is_invoked(self):
        content = self.conversation.messages[-1].msg_content
        try:
            if json.loads(content).keys() >= {'function', 'arguments', 'output'}:
                return True
        except: 
            return False    

    def register_tools(self, tools):
        if not isinstance(tools, list):
            tools=[tools]
        self.tool_manager.register_tools(tools=tools) 


    def _tool_parser(self, **kwargs):
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if self.tool_manager.name_existed(tool):
                    tool = self.tool_manager.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if 'tools' in kwargs:
            if not isinstance(kwargs['tools'], list):
                kwargs['tools']=[kwargs['tools']]
            kwargs['tools'] = lcall(kwargs['tools'], tool_check)

        else:
            tool_kwarg = {"tools": self.tool_manager.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        return kwargs

    async def initiate(self, instruction, system=None, context=None, 
                       name=None, invoke=True, out=True, **kwargs) -> Any:
        if self.tool_manager.registry != {}:
            kwargs = self._tool_parser(**kwargs)
        if self.service is not None:
            await self.service._init()
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self.call_chatcompletion(**config)
        
        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None, 
                       out=True, name=None, invoke=True, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
        else:
            if self.tool_manager.registry != {}:
                kwargs = self._tool_parser(**kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruct, num=3, **kwargs):
        if self.tool_manager.registry != {}:
            kwargs = self._tool_parser(**kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct, tool_choice="auto", tool_parsed=True, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs, tool_parsed=True)

    async def call_chatcompletion(self, schema=oai_schema['chat'], **kwargs):
        messages = [message.msg for message in self.conversation.messages]
        payload = ChatCompletion.create_payload(messages=messages, schema=schema, config=self.llmconfig,**kwargs)
        completion = await self.service.serve(payload=payload)
        if "choices" in completion:
            self.logger_({"input":payload, "output": completion})
            self.conversation.add_messages(response=completion['choices'][0])
            self.conversation.responses.append(self.conversation.messages[-1])
            self.conversation.response_counts += 1
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1
        
    def branch_conversation(self, branch_name: Optional[str] = None) -> None:
        """
        Creates a new branch of the conversation.

        Args:
            branch_name (Optional[str]): The name of the new branch. If None, a name is generated.
        """
        branch_name = branch_name or f"branch_{len(self.branches)}"
        self.branches[branch_name] = self.conversation.clone()

    def switch_branch(self, branch_name: str) -> None:
        """
        Switches the active conversation to a specified branch.

        Args:
            branch_name (str): The name of the branch to switch to.
        """
        if branch_name not in self.branches:
            raise ValueError(f"Branch '{branch_name}' does not exist.")
        self.conversation = self.branches[branch_name]

    def merge_branch(self, source_branch: str, target_branch: str = "main") -> None:
        """
        Merges one branch into another.

        Args:
            source_branch (str): The name of the source branch.
            target_branch (str): The name of the target branch. Defaults to "main".
        """
        if source_branch not in self.branches or target_branch not in self.branches:
            raise ValueError(f"Branch '{source_branch}' or '{target_branch}' does not exist.")
        self.branches[target_branch].merge(self.branches[source_branch])
        if source_branch != "main":
            del self.branches[source_branch]

    async def initiate(self, instruction: str, **kwargs) -> Union[str, None]:
        """
        Starts a new conversation with the given instruction.

        Args:
            instruction (str): The initial instruction to start the conversation.

        Returns:
            Union[str, None]: The AI's response or None if there was no response.
        """
        return await self.follow_up(instruction, **kwargs)

    async def follow_up(self, instruction: str, **kwargs) -> Union[str, None]:
        """
        Continues the conversation with a follow-up instruction.

        Args:
            instruction (str): The follow-up instruction.

        Returns:
            Union[str, None]: The AI's response or None if there was no response.
        """
        instruction_message = Instruction(content=instruction)
        self.conversation.add_message(instruction_message)
        response_content = await self.service.process(
            instruction_message, self.config, **kwargs
        )
        if response_content:
            response_message = Response(content=response_content)
            self.conversation.add_message(response_message)
            return response_content
        return None

    async def auto_follow_up(self, instruction: Optional[str] = None, **kwargs) -> Union[str, None]:
        """
        Automatically continues the conversation using the last response or a given instruction.

        Args:
            instruction (Optional[str]): A specific instruction to use. If None, the last response will be used.

        Returns:
            Union[str, None]: The AI's response or None if there was no response.
        """
        if instruction is None:
            last_response = self.conversation.last_message_of_type(Response)
            instruction = last_response.content if last_response else ""
        
        if instruction:
            return await self.follow_up(instruction, **kwargs)
        return None

    def summarize_branch(self, branch_name: str) -> Dict[str, Any]:
        """
        Summarizes a specific branch of the conversation.

        Args:
            branch_name (str): The name of the branch to summarize.

        Returns:
            Dict[str, Any]: A dictionary containing the summary of the branch.
        """
        if branch_name not in self.branches:
            raise ValueError(f"Branch '{branch_name}' does not exist.")
        branch = self.branches[branch_name]
        return branch.generate_conversation_report()

    def delete_branch(self, branch_name: str) -> None:
        """
        Deletes a branch from the session.

        Args:
            branch_name (str): The name of the branch to delete.
        """
        if branch_name in self.branches and branch_name != "main":
            del self.branches[branch_name]
        else:
            raise ValueError(f"Cannot delete main branch or branch '{branch_name}' does not exist.")

    def get_conversation_history(self, branch_name: Optional[str] = None) -> List[str]:
        """
        Retrieves the conversation history for a branch.

        Args:
            branch_name (Optional[str]): The name of the branch. If None, the main branch is used.

        Returns:
            List[str]: A list containing the messages in the conversation.
        """
        branch = self.branches.get(branch_name, self.conversation)
        return [message.content for message in branch.get_messages()]

    def rollback_conversation(self, steps: int) -> None:
        """
        Rollbacks the conversation to a previous state by the given number of steps.

        Args:
            steps (int): The number of steps to rollback.

        Raises:
            ValueError: If steps are negative or exceed the current number of messages.
        """
        if steps < 0 or steps > len(self.conversation.messages):
            raise ValueError("Steps must be a non-negative integer less than or equal to the number of messages.")
        self.conversation.messages = self.conversation.messages[:-steps].reset_index(drop=True)

    def get_current_state(self) -> Dict[str, Union[str, int]]:
        """
        Extracts the current state of the conversation.

        Returns:
            Dict[str, Union[str, int]]: A dictionary containing the total number of messages and the last message.
        """
        last_message = self.conversation.messages.iloc[-1]["content"] if not self.conversation.messages.empty else None
        return {
            "total_messages": len(self.conversation.messages),
            "last_message": last_message
        }

    def get_detailed_conversation_history(self, branch_name: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves a detailed conversation history for a branch including timestamps and roles.

        Args:
            branch_name (Optional[str]): The branch name to get history for. If None, the main branch is used.

        Returns:
            pd.DataFrame: A DataFrame containing the detailed conversation history.
        """
        branch = self.branches.get(branch_name, self.conversation)
        return branch.messages[["timestamp", "role", "name", "content"]]

    def save_session(self, filepath: str) -> None:
        """
        Saves the session to a file.

        Args:
            filepath (str): The path to the file where the session will be saved.
        """
        session_data = {
            "system": self.system,
            "config": self.config.to_json(),
            "conversation": self.conversation.to_json(),
            "branches": {name: branch.to_json() for name, branch in self.branches.items()},
        }
        with open(filepath, "w") as file:
            json.dump(session_data, file)

    def end_session(self, archive_path: Optional[str] = None) -> None:
        """
        Ends the session and optionally archives the main conversation.

        Args:
            archive_path (Optional[str]): The path where the conversation archive will be saved, if desired.
        """
        if archive_path:
            self.conversation.archive_conversation(archive_path)
        self.branches = {"main": self.conversation}
        