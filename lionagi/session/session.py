import aiohttp
import asyncio
import json
from typing import Any

from .conversation import Conversation
from ..utils.sys_util import to_list
from ..utils.log_util import DataLogger
from ..utils.api_util import StatusTracker
from ..utils.tool_util import ToolManager
from ..api.oai_service import OpenAIService

from ..api.oai_config import oai_llmconfig


status_tracker = StatusTracker()
OAIService = OpenAIService()

class Session():
    """
    A class representing a conversation session with a conversational AI system.

    This class manages the flow of conversation, system settings, and interactions with external tools.

    Attributes:
        conversation (Conversation): An instance of the Conversation class to manage messages.
        system (str): The current system setting for the conversation.
        llmconfig (dict): Configuration settings for the language model.
        _logger (DataLogger): An instance of the DataLogger class for logging conversation details.
        api_service: An instance of the API service for making calls to the conversational AI model.
        toolmanager (ToolManager): An instance of the ToolManager class for managing external tools.

    Methods:
        set_dir(dir):
            Set the directory for logging.

        set_system(system):
            Set the system for the conversation.

        set_llmconfig(llmconfig):
            Set the language model configuration.

        set_api_service(api_service):
            Set the API service for making model calls.

        _output(output, invoke=True, out=True) -> Any:
            Process the output, invoke tools if needed, and optionally return the output.

        register_tools(tools, funcs, update=False, new=False, prefix=None, postfix=None):
            Register tools and their corresponding functions.

        initiate(instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
            Start a new conversation session with the provided instruction.

        followup(instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
            Continue the conversation with the provided instruction.

        create_payload_chatcompletion(**kwargs) -> dict:
            Create a payload for chat completion based on the conversation state and configuration.

        call_chatcompletion(sleep=0.1, **kwargs) -> None:
            Make a call to the chat completion API and process the response.

        messages_to_csv(dir=None, filename="_messages.csv", **kwargs) -> None:
            Save conversation messages to a CSV file.

        log_to_csv(dir=None, filename="_llmlog.csv", **kwargs) -> None:
            Save conversation logs to a CSV file.
    """
    
    def __init__(self, system, dir=None, llmconfig=oai_llmconfig, api_service=OAIService):
        """
        Initialize a Session object with default or provided settings.

        Parameters:
            system (str): The initial system setting for the conversation.
            dir (Optional[str]): The directory for logging. Default is None.
            llmconfig (Optional[dict]): Configuration settings for the language model. Default is oai_llmconfig.
            api_service: An instance of the API service for making calls to the conversational AI model.
        """
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self._logger = DataLogger(dir=dir)
        self.api_service = api_service
        self.toolmanager = ToolManager()
    
    def set_dir(self, dir):
        """
        Set the directory for logging.

        Parameters:
            dir (str): The directory path.
        """
        self._logger.dir = dir
    
    def set_system(self, system):
        """
        Set the system for the conversation.

        Parameters:
            system (str): The system setting.
        """
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        """
        Set the language model configuration.

        Parameters:
            llmconfig (dict): Configuration settings for the language model.
        """
        self.llmconfig = llmconfig
    
    def set_api_service(self, api_service):
        """
        Set the API service for making model calls.

        Parameters:
            api_service: An instance of the API service.
        """
        self.api_service = api_service
    
    async def _output(self, invoke=True, out=True, tool_parser=None):
        """
        Process the output, invoke tools if needed, and optionally return the output.

        Parameters:
            output: The output to process.
            invoke (bool): Whether to invoke tools based on the output. Default is True.
            out (bool): Whether to return the output. Default is True.

        Returns:
            Any: The processed output.
        """
        if invoke:
            try: 
                func, args = self.toolmanager._get_function_call(self.conversation.responses[-1]['content'])
                outs = await self.toolmanager.ainvoke(func, args)
                outs = tool_parser(outs) if tool_parser else outs
                self.conversation.add_messages(response=outs)
            except:
                pass
        if out:
            return self.conversation.responses[-1]['content']
        
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
        self.toolmanager.register_tools(tools, funcs, update, new, prefix, postfix)
    
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, tool_parser=None, **kwargs) -> Any:
        """
        Start a new conversation session with the provided instruction.

        Parameters:
            instruction (str): The instruction to initiate the conversation.
            system (Optional[str]): The system setting for the conversation. Default is None.
            context (Optional[dict]): Additional context for the instruction. Default is None.
            out (bool): Whether to return the output. Default is True.
            name (Optional[str]): The name associated with the instruction. Default is None.
            invoke (bool): Whether to invoke tools based on the output. Default is True.
            kwargs: Additional keyword arguments for configuration.

        Returns:
            Any: The processed output.
        """
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self.call_chatcompletion(**config)
        
        return await self._output(invoke, out, tool_parser)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, tool_parser=None, **kwargs) -> Any:
        """
        Continue the conversation with the provided instruction.

        Parameters:
            instruction (str): The instruction to continue the conversation.
            system (Optional[str]): The system setting for the conversation. Default is None.
            context (Optional[dict]): Additional context for the instruction. Default is None.
            out (bool): Whether to return the output. Default is True.
            name (Optional[str]): The name associated with the instruction. Default is None.
            invoke (bool): Whether to invoke tools based on the output. Default is True.
            kwargs: Additional keyword arguments for configuration.

        Returns:
            Any: The processed output.
        """
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        
        return await self._output(invoke, out, tool_parser)
    
    def create_payload_chatcompletion(self, **kwargs):
        """
        Create a payload for chat completion based on the conversation state and configuration.

        Parameters:
            kwargs: Additional keyword arguments for configuration.

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

    async def call_chatcompletion(self, sleep=0.1,  **kwargs):
        """
        Make a call to the chat completion API and process the response.

        Parameters:
            sleep (float): The sleep duration after making the API call. Default is 0.1.
            kwargs: Additional keyword arguments for configuration.
        """
        endpoint = f"chat/completions"
        try:
            async with aiohttp.ClientSession() as session:
                payload = self.create_payload_chatcompletion(**kwargs)
                completion = await self.api_service.call_api(
                                session, endpoint, payload)
                if "choices" in completion:
                    self._logger({"input":payload, "output": completion})
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
    
    def messages_to_csv(self, dir=None, filename="_messages.csv", **kwags):
        """
        Save conversation messages to a CSV file.

        Parameters:
            dir (Optional[str]): The directory path for saving the CSV file. Default is None.
            filename (Optional[str]): The filename for the CSV file. Default is "_messages.csv".
            kwargs: Additional keyword arguments for CSV file settings.
        """
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwags)
        
    def log_to_csv(self, dir=None, filename="_llmlog.csv", **kwags):
        """
        Save conversation logs to a CSV file.

        Parameters:
            dir (Optional[str]): The directory path for saving the CSV file. Default is None.
            filename (Optional[str]): The filename for the CSV file. Default is "_llmlog.csv".
            kwargs: Additional keyword arguments for CSV file settings.
        """
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self._logger.to_csv(dir=dir, filename=filename, **kwags)

    def is_invoked(self):
        msg = self.conversation.messages[-1]
        try: 
            if "function call result" in json.loads(msg['content']).keys():
                return True
        except: 
            return False

    async def auto_followup(self, instruct, num=3, tool_parser=None, **kwags):
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct,tool_parser=tool_parser, tool_choice="auto", **kwags)
            num -= 1
            cont_ = True if self.is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwags)