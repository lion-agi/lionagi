import json
import pandas as pd

from typing import Any, Callable, Dict, List, Optional, Union
from collections import deque
import asyncio
from dotenv import load_dotenv

from lionagi.utils import as_dict, get_flattened_keys, alcall, lcall, to_list
from lionagi.utils.sys_util import is_same_dtype
from lionagi.schema import Tool
from lionagi._services.base_service import StatusTracker, BaseService
from lionagi._services.oai import OpenAIService
from lionagi._services.openrouter import OpenRouterService

from lionagi.configs.oai_configs import oai_schema
from lionagi.configs.openrouter_configs import openrouter_schema
from lionagi.tools.tool_manager import ToolManager

from ..messages.messages import Instruction, System
from ..instruction_set.instruction_set import InstructionSet

from .conversation import Conversation, validate_messages
from .branch_manager import Request

load_dotenv()


class Branch(Conversation):
    
    def __init__(
        self,
        name: Optional[str] = None,
        messages: Optional[pd.DataFrame] = None,
        instruction_sets: Optional[Dict[str, InstructionSet]] = None,
        tool_manager: Optional[ToolManager] = None,
        service : Optional[BaseService] = None,
        llmconfig: Optional[Dict] = None,
    ):

        super().__init__()
        self.messages = (
            messages
            if messages is not None
            else pd.DataFrame(
                columns=["node_id", "role", "sender", "timestamp", "content"]
            )
        )
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()
        self.status_tracker = StatusTracker()
        self._add_service(service, llmconfig)
        self.name = name
        self.pending_ins = {}
        self.pending_outs = deque()

    @property
    def chat_messages(self):
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self):
        return self._to_chatcompletion_message(with_sender=True) 

    @property
    def messages_describe(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "summary_by_sender": self._info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    @property
    def has_tools(self) -> bool:
        return self.tool_manager.registry != {}

# ----- tool manager methods ----- #

    def register_tools(self, tools: Union[Tool, List[Tool]]):
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, tools: Union[Tool, List[Tool], str, List[str]], verbose=True) -> bool:
        if isinstance(tools, list):
            if is_same_dtype(tools, str):
                for tool in tools:
                    if tool in self.tool_manager.registry:
                        self.tool_manager.registry.pop(tool)
                if verbose:
                    print("tools successfully deleted")
                return True
            elif is_same_dtype(tools, Tool):
                for tool in tools:
                    if tool.name in self.tool_manager.registry:
                        self.tool_manager.registry.pop(tool.name)
                if verbose:
                    print("tools successfully deleted")
                return True
        if verbose:
            print("tools deletion failed")
        return False

# ----- branch manipulation ----- #
    def clone(self) -> 'Branch':
        cloned = Branch(
            messages=self.messages.copy(), 
            instruction_sets=self.instruction_sets.copy(),
            tool_manager=ToolManager()
        )
        tools = [
            tool for tool in self.tool_manager.registry.values()]
        
        cloned.register_tools(tools)

        return cloned

    def merge_branch(self, branch: 'Branch', update: bool = True):

        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how='outer')

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(
                branch.tool_manager.registry
            )
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value


# ----- intra-branch communication methods ----- #
    def send(self, to_name, title, package):
        """
        Send a request package to a specified recipient.

        Args:
            to_name (str): The name of the recipient.
            title (str): The title or category of the request (e.g., 'messages', 'tool', 'service', 'llmconfig').
            package (Any): The actual data or object to be sent. Its expected type depends on the title.
        """
        request = Request(from_name=self.name, to_name=to_name, title=title, request=package)
        self.pending_outs.append(request)

    def receive(self, from_name, messages=True, tool=True, service=True, llmconfig=True):
        """
        Process and integrate received request packages based on their titles.

        Args:
            from_name (str): The name of the sender whose packages are to be processed.
            messages (bool, optional): If True, processes 'messages' requests.
            tool (bool, optional): If True, processes 'tool' requests.
            service (bool, optional): If True, processes 'service' requests.
            llmconfig (bool, optional): If True, processes 'llmconfig' requests.

        Raises:
            ValueError: If no package is found from the specified sender, or if any of the packages have an invalid format.
        """
        skipped_requests = deque()
        if from_name not in self.pending_ins:
            raise ValueError(f'No package from {from_name}')
        while self.pending_ins[from_name]:
            request = self.pending_ins[from_name].popleft()

            if request.title == 'messages' and messages:
                if not isinstance(request.request, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                validate_messages(request.request)
                self.messages = self.messages.merge(request.request, how='outer')
                continue

            elif request.title == 'tool' and tool:
                if not isinstance(request.request, Tool):
                    raise ValueError('Invalid tool format')
                self.tool_manager.register_tools([request.request])

            elif request.title == 'service' and service:
                if not isinstance(request.request, BaseService):
                    raise ValueError('Invalid service format')
                self.service = request.request

            elif request.title == 'llmconfig' and llmconfig:
                if not isinstance(request.request, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(request.request)

            else:
                skipped_requests.append(request)

        self.pending_ins[from_name] = skipped_requests

    def receive_all(self):
        """
        Process all pending incoming requests from all senders.
        """
        for key in list(self.pending_ins.keys()):
            self.receive(key)
       

# ----- service methods ----- #

    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
        messages = self.chat_messages if not with_sender else self.chat_messages_with_sender
        payload, completion = await self.service.serve_chat(
            messages=messages, **kwargs)
        if "choices" in completion:
            add_msg_config = {"response":completion['choices'][0]}
            if sender is not None:
                add_msg_config["sender"] = sender
                
            self.add_message(**add_msg_config)
            self.status_tracker.num_tasks_succeeded += 1
        else:
            self.status_tracker.num_tasks_failed += 1

# ----- chat methods ----- #

    async def chat(
        self,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs
    ) -> Any:
        
        if system:
            self.change_first_system_message(system)
        self.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if tools and self.has_tools:
                kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

        config = {**self.llmconfig, **kwargs}
        if sender is not None: 
            config.update({"sender": sender})
        
        await self.call_chatcompletion(**config)
        
        async def _output():
            content_ = as_dict(self.messages.content.iloc[-1])
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [as_dict(i) for i in tool_uses["action_list"]], 
                        self.tool_manager.get_function_call
                    )
                    
                    outs = await alcall(func_calls, self.tool_manager.invoke)
                    outs = to_list(outs, flatten=True)

                    for out_, f in zip(outs, func_calls):
                        self.add_message(
                            response={
                                "function": f[0], 
                                "arguments": f[1], 
                                "output": out_
                            }
                        )
                except:
                    pass
            if out:
                if (
                    len(content_.items()) == 1 
                    and len(get_flattened_keys(content_)) == 1
                ):
                    key = get_flattened_keys(content_)[0]
                    return content_[key]
                return content_
        
        return await _output()

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools = None, 
        num_rounds: int = 1,
        fallback: Optional[Callable] = None,
        fallback_kwargs: Optional[Dict] = None,
        out=True,
        **kwargs 
    ):
        """
        one reason step and one action step is considered one round. 
        ReAct will reason then action for specified number of rounds, 
        and then present final output.
        
        so: 1 round, will be 3 messages
            2 round, will be 5 messages
        """
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                self.register_tools(tools)
        
        if self.tool_manager.registry == {}:
            raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")
        
        else:
            kwargs = self.tool_manager._tool_parser(tools=True, **kwargs)

        i = 0
        while i < num_rounds:
            prompt = f"""
                you have {(num_rounds-i)*2} step left in current task. reflect, perform 
                reason for action plan according to available tools only, 
                apply divide and conquer technique
            """ 
            instruct = {"Notice": prompt}
            
            if i == 0:
                instruct["Task"] = instruction
                await self.chat(
                    instruction=instruct, context=context, tool_parsed=True,
                    system=system, out=False, sender=sender, **kwargs
                )
        
            elif i >0:
                await self.chat(
                    instruction=instruct, out=False, tool_parsed=True, sender=sender, **kwargs
                )
                
            prompt = f"""
                you have {(num_rounds-i)*2-1} step left in current task, 
                invoke tool usage according to plan and perform the actions
            """
            await self.chat(prompt, tool_choice="auto", tool_parsed=True, out=False,sender=sender, **kwargs)

            i += 1
        
        if self._is_invoked():
            if fallback is not None:
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(**fallback_kwargs)
                else:
                    return fallback(**fallback_kwargs)
            prompt = """
                present the final result to user
            """
            return await self.chat(prompt, sender=sender, tool_parsed=True, **kwargs)
        else:
            if out:
                return self.last_response_content

    async def auto_ReAct(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools = None, 
        max_rounds: int = 1,
        
        fallback: Optional[Callable] = None,
        fallback_kwargs: Optional[Dict] = None,
        **kwargs 
    ):
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                self.register_tools(tools)
        
        if self.tool_manager.registry == {}:
            raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")
        
        else:
            kwargs = self.tool_manager._tool_parser(tools=True, **kwargs)

        i = 0
        while i < max_rounds:
            prompt = f"""
                you have {(max_rounds-i)*2} step left in current task. reflect, perform 
                reason for action plan according to available tools only, apply divide and conquer technique
            """ 
            instruct = {"Notice": prompt}
            
            if i == 0:
                instruct["Task"] = instruction
                await self.chat(
                    instruction=instruct, context=context, 
                    system=system, out=False, sender=sender, **kwargs
                )
        
            elif i >0:
                await self.chat(
                    instruction=instruct, out=False, sender=sender, **kwargs
                )
                
            prompt = f"""
                you have {(max_rounds-i)*2-1} step left in current task, invoke tool usage to perform the action
            """
            out = await self.chat(prompt, tool_choice="auto", tool_parsed=True, out=False,sender=sender, **kwargs)
            if not self._is_invoked():
                return out

            i += 1

        if self._is_invoked():
            if fallback is not None:
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(**fallback_kwargs)
                else:
                    return fallback(**fallback_kwargs)
            prompt = """
                present the final result to user
            """
            return await self.chat(prompt, sender=sender, tool_parsed=True, **kwargs)

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True, 
        **kwargs
    ) -> None:

        """
        auto tool usages until LLM decides done. Then presents final results. 
        """

        if self.tool_manager.registry != {} and tools:
            kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
                if further actions are needed, invoke tools usage. If you are done, present the final result 
                to user without further tool usage
            """
            if n_tries > 0:
                _out = await self.chat(prompt, sender=sender, tool_choice="auto", tool_parsed=True, **kwargs)
                n_tries += 1
                
                if not self._is_invoked():
                    return _out if out else None
                                
            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                out = await self.chat(
                    instruct, context=context, system=system, sender=sender, tool_choice="auto", 
                    tool_parsed=True, **kwargs
                )
                n_tries += 1
                
                if not self._is_invoked():
                    return _out if out else None

        if self._is_invoked():
            """
            In the current task, you are at your last step, present the final result to user
            """
            return await self.chat(instruction, sender=sender, tool_parsed=True, **kwargs)

    async def followup(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True, 
        **kwargs
    ) -> None:

        """
        auto tool usages until LLM decides done. Then presents final results. 
        """

        if self.tool_manager.registry != {} and tools:
            kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
                if further actions are needed, invoke tools usage. If you are done, present the final result 
                to user without further tool usage.
            """
            if n_tries > 0:
                _out = await self.chat(prompt, sender=sender, tool_choice="auto", tool_parsed=True, **kwargs)
                n_tries += 1
                
                if not self._is_invoked():
                    return _out if out else None
                                
            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                out = await self.chat(
                    instruct, context=context, system=system, sender=sender, tool_choice="auto", 
                    tool_parsed=True, **kwargs
                )
                n_tries += 1
                
                if not self._is_invoked():
                    return _out if out else None

    def _add_service(self, service, llmconfig):
        service = service or OpenAIService()
        self.service=service
        if llmconfig:
            self.llmconfig = llmconfig
        else:
            if isinstance(service, OpenAIService):
                self.llmconfig = oai_schema["chat/completions"]["config"]
            elif isinstance(service, OpenRouterService):
                self.llmconfig = openrouter_schema["chat/completions"]["config"]
            else:
                self.llmconfig = {}


    def _to_chatcompletion_message(self, with_sender=False) -> List[Dict[str, Any]]:
        message = []

        for _, row in self.messages.iterrows():
            content_ = row['content']
            if content_.startswith('Sender'):
                content_ = content_.split(':', 1)[1]
                
            if isinstance(content_, str):
                try:
                    content_ = json.dumps(as_dict(content_))
                except Exception as e:
                    raise ValueError(f"Error in serealizing, {row['node_id']} {content_}: {e}")
                
            out = {"role": row['role'], "content": content_}
            if with_sender:
                out['content'] = f"Sender {row['sender']}: {content_}"
            
            message.append(out)
        return message


    def _is_invoked(self) -> bool:
        """
        Check if the conversation has been invoked with an action response.

        Returns:
            bool: True if the conversation has been invoked, False otherwise.

        """
        content = self.messages.iloc[-1]['content']
        try:
            if (
                as_dict(content)['action_response'].keys() >= {'function', 'arguments', 'output'}
            ):
                return True
        except:
            return False




    # def add_instruction_set(self, name: str, instruction_set: InstructionSet):
    #     """
    #     Add an instruction set to the conversation.
    #
    #     Args:
    #         name (str): The name of the instruction set.
    #         instruction_set (InstructionSet): The instruction set to add.
    #
    #     Examples:
    #         >>> branch.add_instruction_set("greet", InstructionSet(instructions=["Hello", "Hi"]))
    #     """
    #     self.instruction_sets[name] = instruction_set

    # def remove_instruction_set(self, name: str) -> bool:
    #     """
    #     Remove an instruction set from the conversation.
    #
    #     Args:
    #         name (str): The name of the instruction set to remove.
    #
    #     Returns:
    #         bool: True if the instruction set was removed, False otherwise.
    #
    #     Examples:
    #         >>> branch.remove_instruction_set("greet")
    #         True
    #     """
    #     return self.instruction_sets.pop(name)

    # async def instruction_set_auto_followup(
    #     self,
    #     instruction_set: InstructionSet,
    #     num: Union[int, List[int]] = 3,
    #     **kwargs
    # ) -> None:
    #     """
    #     Automatically perform follow-up chats for an entire instruction set.
    #
    #     This method asynchronously conducts follow-up chats for each instruction in the provided instruction set,
    #     handling tool invocations as specified.
    #
    #     Args:
    #         instruction_set (InstructionSet): The instruction set to process.
    #         num (Union[int, List[int]]): The maximum number of follow-up chats to perform for each instruction,
    #                                       or a list of maximum numbers corresponding to each instruction.
    #         **kwargs: Additional keyword arguments to pass to the chat completion service.
    #
    #     Raises:
    #         ValueError: If the length of `num` as a list does not match the number of instructions in the set.
    #
    #     Examples:
    #         >>> instruction_set = InstructionSet(instructions=["What's the weather?", "And for tomorrow?"])
    #         >>> await branch.instruction_set_auto_followup(instruction_set)
    #     """
    #
    #     if isinstance(num, List):
    #         if len(num) != instruction_set.instruct_len:
    #             raise ValueError(
    #                 'Unmatched auto_followup num size and instructions set size'
    #             )
    #     current_instruct_node = instruction_set.get_instruction_by_id(
    #         instruction_set.first_instruct
    #     )
    #     for i in range(instruction_set.instruct_len):
    #         num_ = num if isinstance(num, int) else num[i]
    #         tools = instruction_set.get_tools(current_instruct_node)
    #         if tools:
    #             await self.auto_followup(
    #                 current_instruct_node, num=num_, tools=tools, self=self, **kwargs
    #             )
    #         else:
    #             await self.chat(current_instruct_node)
    #         current_instruct_node = instruction_set.get_next_instruction(
    #             current_instruct_node
    #         )
