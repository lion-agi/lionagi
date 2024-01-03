import json
import aiohttp
import asyncio
from typing import Any
from dotenv import load_dotenv


from lionagi.utils.type_util import to_list
from lionagi.utils.call_util import alcall, lcall







from .conversations import Conversation
from ..schema.data_logger import DataLogger
from lionagi.objs import PayloadMaker, StatusTracker, ToolRegistry
from ..services import OpenAIService
from lionagi.objs.status_tracker import StatusTracker



load_dotenv()
OAIService = OpenAIService()
status_tracker = StatusTracker()


class Session:

    
    def __init__(self, system, dir=None, llmconfig=None, service=OAIService):

        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig or service.default_schema['config']
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.tool_registry = ToolRegistry()
    
    def set_dir(self, dir):
        self.logger_.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        """
        Set the API service for making model calls.

        Parameters:
            api_service: An instance of the API service.
        """
        self.service = service
    
    async def _output(self, invoke=True, out=True, tool_parser=None):
        """
        Process the output, invoke tools if needed, and optionally return the output.

        Parameters:
            invoke (bool): Whether to invoke tools based on the output. Default is True.

            out (bool): Whether to return the output. Default is True.

        Returns:
            Any: The processed output.
        """
        if invoke:
            try:
                tool_uses = json.loads(self.conversation.responses[-1]['content'])
                if 'function_list' in tool_uses.keys():
                    func_calls = lcall(tool_uses['function_list'], self.tool_registry._get_function_call)

                else:
                    func_calls = lcall(tool_uses['tool_uses'], self.tool_registry._get_function_call)

                outs = await alcall(func_calls, self.tool_registry.ainvoke)
                if tool_parser:
                    outs = lcall(outs, tool_parser)
                for out, f in zip(outs, func_calls):
                    response = {"function": f[0], "arguments": f[1], "output": out}
                    self.conversation.add_messages(response=response)

            except:
                pass

        if out:
            return self.conversation.responses[-1]['content']
    
    def _is_invoked(self):
        """
        Checks if the current message indicates the invocation of a function call.

        Returns:
            bool: True if a function call is detected in the content of the last message, False otherwise.
        """
        msg = self.conversation.messages[-1]
        try: 
            if json.loads(msg['content']).keys() >= {'function', 'arguments', 'output'}:
                return True
        except: 
            return False    

    def register_tools(self, tools, funcs, update=False, new=False, prefix=None, postfix=None):
        """
        Register tools and their corresponding functions.

        Parameters:
            tools (list): The list of tool information dictionaries.

            funcs (list): The list of corresponding functions.

            update (bool): Whether to update existing functions.

            new (bool): Whether to create new registries for existing functions.

            prefix (Optional[str]): A prefix to add to the function names.

            postfix (Optional[str]): A postfix to add to the function names.
        """
        funcs = to_list(funcs)
        self.tool_registry.register_tools(tools, funcs, update, new, prefix, postfix)
    
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, tool_parser=None, **kwargs) -> Any:
        """
        Start a new conversation session with the provided instruction.

        Parameters:
            instruction (Union[str, dict]): The instruction to initiate the conversation.

            system (Optional[str]): The system setting for the conversation. Default is None.

            context (Optional[dict]): Additional context for the instruction. Default is None.

            out (bool): Whether to return the output. Default is True.

            name (Optional[str]): The name associated with the instruction. Default is None.

            invoke (bool): Whether to invoke tools based on the output. Default is True.

            tool_parser (Optional[callable]): A custom tool parser function. Default is None.

            **kwargs: Additional keyword arguments for configuration.

        Returns:
            Any: The processed output.
        """
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self._call_chatcompletion(**config)
        
        return await self._output(invoke, out, tool_parser)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, tool_parser=None, **kwargs) -> Any:
        """
        Continue the conversation with the provided instruction.

        Parameters:
            instruction (Union[str, dict]): The instruction to continue the conversation.

            system (Optional[str]): The system setting for the conversation. Default is None.

            context (Optional[dict]): Additional context for the instruction. Default is None.

            out (bool): Whether to return the output. Default is True.

            name (Optional[str]): The name associated with the instruction. Default is None.

            invoke (bool): Whether to invoke tools based on the output. Default is True.

            tool_parser (Optional[callable]): A custom tool parser function. Default is None.

            **kwargs: Additional keyword arguments for configuration.

        Returns:
            Any: The processed output.
        """
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self._call_chatcompletion(**config)

        return await self._output(invoke, out, tool_parser)

    async def auto_followup(self, instruct, num=3, tool_parser=None, **kwargs):
        """
        Automates the follow-up process for a specified number of times or until the session concludes.

        Parameters:
            instruct (Union[str, dict]): The instruction for the follow-up.

            num (int, optional): The number of times to automatically follow up. Defaults to 3.

            tool_parser (callable, optional): A custom tool parser function. Defaults to None.

            **kwargs: Additional keyword arguments passed to the underlying `followup` method.

        """
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct, tool_parser=tool_parser, tool_choice="auto", **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs)

    def _create_payload_chatcompletion(self, **kwargs):
        """
        Create a payload for chat completion based on the conversation state and configuration.

        Parameters:
            **kwargs: Additional keyword arguments for configuration.

        Returns:
            dict: The payload for chat completion.
        """
        # currently only openai chat completions are supported
        messages = self.conversation.messages
        config = {**self.llmconfig, **kwargs}
        payload = {
            "messages": messages,
            "model": config.get('model'),
            "frequency_penalty": config.get('frequency_penalty'),
            "n": config.get('n'),
            "presence_penalty": config.get('presence_penalty'),
            "response_format": config.get('response_format'),
            "temperature": config.get('temperature'),
            "top_p": config.get('top_p'),
            }
        
        for key in ["seed", "stop", "stream", "tools", "tool_choice", "user", "max_tokens"]:
            if bool(config[key]) is True and str(config[key]) != "none":
                payload.update({key: config[key]})
        return payload

    async def _call_chatcompletion(self, sleep=0.1,  **kwargs):
        """
        Make a call to the chat completion API and process the response.

        Parameters:
            sleep (float): The sleep duration after making the API call. Default is 0.1.

            **kwargs: Additional keyword arguments for configuration.
        """
        endpoint = f"chat/completions"
        try:
            async with aiohttp.ClientSession() as session:
                payload = self._create_payload_chatcompletion(**kwargs)
                completion = await self.service.call_api(
                                session, endpoint, payload)
                if "choices" in completion:
                    self.logger_({"input": payload, "output": completion})
                    self.conversation.add_messages(response=completion['choices'][0])
                    self.conversation.responses.append(self.conversation.messages[-1])
                    self.conversation.response_counts += 1
                    await asyncio.sleep(sleep)
                    status_tracker.num_tasks_succeeded += 1
                else:
                    status_tracker.num_tasks_failed += 1
        except Exception as e:
            status_tracker.num_tasks_failed += 1
            raise e
    
    def messages_to_csv(self, dir=None, filename="_messages.csv", **kwargs):
        """
        Save conversation messages to a CSV file.

        Parameters:
            dir (Optional[str]): The directory path for saving the CSV file. Default is None.

            filename (Optional[str]): The filename for the CSV file. Default is "_messages.csv".

            **kwargs: Additional keyword arguments for CSV file settings.
        """
        dir = dir or self.logger_.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    def log_to_csv(self, dir=None, filename="_llmlog.csv", **kwargs):
        """
        Save conversation logs to a CSV file.

        Parameters:
            dir (Optional[str]): The directory path for saving the CSV file. Default is None.

            filename (Optional[str]): The filename for the CSV file. Default is "_llmlog.csv".

            **kwargs: Additional keyword arguments for CSV file settings.
        """
        dir = dir or self.logger_.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.logger_.to_csv(dir=dir, filename=filename, **kwargs)