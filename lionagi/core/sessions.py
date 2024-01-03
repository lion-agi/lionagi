import json
from typing import Any
from dotenv import load_dotenv

from ..schema import DataLogger
from ..utils import lcall, alcall
from ..services import OpenAIService, ChatCompletion
from ..core.conversations import Conversation
from ..objs.tool_registry import ToolManager
from ..configs.oai_configs import oai_schema

load_dotenv()
OAIService = OpenAIService()


class Session:
    """
    The Session class is responsible for managing a conversation session with a given system,
    handling the logging of data, and invoking tools as part of the conversation.

    Attributes:
        conversation (Conversation): An object to manage the conversation flow and history.
        
        system (str): The name of the system with which the conversation is happening.
        
        llmconfig (dict): Configuration for the language model.
        
        _logger (DataLogger): An object for logging conversation data.
        
        service (OpenAIService): A service object for interacting with OpenAI APIs.
        
        tool_manager (ToolManager): An object to manage the registration and invocation of tools.
    """

    def __init__(
        self, system, dir=None, llmconfig=oai_schema['chat']['config'], 
        service=OAIService
        ):
        """
        Initializes the Session object.

        Args:
            system (str): The name of the system with which the session is initiated.
            
            dir (str, optional): The directory for saving logs. Defaults to None.
            
            llmconfig (dict): Configuration for the language model. Defaults to chat config schema.
            
            service (OpenAIService): The service object for API interactions. Defaults to an instance of OpenAIService.
        """

        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.tool_manager = ToolManager()
    
    def set_dir(self, dir):
        """
        Sets the directory where data logs should be saved.
        
        Args:
            dir (str): The path to the directory for saving logs.
        """
        self.logger_.dir = dir
    
    def set_system(self, system):
        """
        Changes the system associated with the conversation.
        
        Args:
            system (str): The name of the new system for the conversation.
        """
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        """
        Updates the language model configuration.
        
        Args:
            llmconfig (dict): The new configuration for the language model.
        """
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        """
        Sets the service object used for API interactions.
        
        Args:
            service (OpenAIService): The new service object.
        """
        self.service = service
    
    async def _output(self, invoke=True, out=True):
        """
        Processes the output from the conversation, possibly invoking tools and returning the latest response.
        
        Args:
            invoke (bool): Indicates whether to invoke tools based on the latest response. Defaults to True.
            
            out (bool): Determines whether to return the latest response content. Defaults to True.
        
        Returns:
            The content of the latest response if out is True. Otherwise, returns None.
        """
        if invoke:
            try: 
                # func, args = self.tool_manager._get_function_call(self.conversation.responses[-1]['content'])
                # outs = await self.tool_manager.invoke(func, args)
                # self.conversation.add_messages(response=outs)

                tool_uses = json.loads(self.conversation.responses[-1]['content'])
                if 'function_list' in tool_uses.keys():
                    func_calls = lcall(tool_uses['function_list'], self.tool_manager._get_function_call)
                else:
                    func_calls = lcall(tool_uses['tool_uses'], self.tool_manager._get_function_call)

                outs = await alcall(func_calls, self.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    response = {"function": f[0], "arguments": f[1], "output": out}
                    self.conversation.add_messages(response=response)

            except:
                pass
        if out:
            return self.conversation.responses[-1]['content']
    
    def _is_invoked(self):
        """
        Checks if the last message in the conversation indicates a function call result.
        
        Returns:
            bool: True if the last message is a function call result, False otherwise.
        """
        msg = self.conversation.messages[-1]
        try: 
            if "function call result" in json.loads(msg['content']).keys():
                return True
        except: 
            return False    

    def register_tools(self, tools, update=False, new=False, prefix=None, postfix=None):
        """
        Registers a list of tools to the tool manager and updates the language model configuration.
        
        Args:
            tools: A single tool or a list of tools to be registered.
            update (bool): If True, update existing tools. Defaults to False.
            new (bool): If True, add as new tools. Defaults to False.
            prefix: A prefix added to all tool names. Defaults to None.
            postfix: A postfix added to all tool names. Defaults to None.
        """
        if not isinstance(tools, list):
            tools=[tools]
        self.tool_manager.register_tools(tools=tools, update=update, new=new, prefix=prefix, postfix=postfix)
        tools_schema = lcall(tools, lambda tool: tool.to_dict()['schema_'])
        if self.llmconfig['tools'] is None:
            self.llmconfig['tools'] = tools_schema
        else:
            self.llmconfig['tools'] += tools_schema
    
    async def initiate(self, instruction, system=None, context=None, 
                       name=None, invoke=True, out=True, **kwargs) -> Any:
        """
        Initiates a conversation with an instruction and possibly additional context.
        
        Args:
            instruction (str): The initial instruction for the conversation.
            system (str, optional): The name of the system to be used. If None, defaults to current system.
            context (str, optional): Additional context for the conversation. Defaults to None.
            name (str, optional): The name associated with the conversation. Defaults to None.
            invoke (bool): Indicates whether to invoke tools. Defaults to True.
            out (bool): Determines whether to return the latest response content. Defaults to True.
            **kwargs: Additional keyword arguments for language model configuration.
        
        Returns:
            The output of the conversation if out is True, otherwise None.
        """
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self.call_chatcompletion(**config)
        
        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None, 
                       out=True, name=None, invoke=True, **kwargs) -> Any:
        """
        Continues the conversation with a follow-up instruction.
        
        Args:
            instruction (str): The follow-up instruction for the conversation.
            system (str, optional): The name of the system to be used. If None, defaults to current system.
            context (str, optional): Additional context for the conversation. Defaults to None.
            out (bool): Determines whether to return the latest response content. Defaults to True.
            name (str, optional): The name associated with the conversation. Defaults to None.
            invoke (bool): Indicates whether to invoke tools. Defaults to True.
            **kwargs: Additional keyword arguments for language model configuration.
        
        Returns:
            The output of the conversation if out is True, otherwise None.
        """
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruct, num=3, **kwargs):
        """
        Automatically generates follow-up messages based on whether the last response invoked a tool.
        
        Args:
            instruct (str): The instruction to pass for follow-up.
            num (int): The number of follow-ups to attempt. Defaults to 3.
            **kwargs: Additional keyword arguments for the follow-up process.
        """
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct, tool_choice="auto", **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs)

    def messages_to_csv(self, dir=None, filename="messages.csv", **kwargs):
        """
        Exports the conversation messages to a CSV file.
        
        Args:
            dir (str, optional): The directory where the CSV should be saved. Defaults to the logger's directory.
            filename (str): The name of the CSV file. Defaults to "messages.csv".
            **kwargs: Additional keyword arguments passed to the CSV writing function.
        
        Raises:
            ValueError: If no directory is specified.
        """
        dir = dir or self.logger_.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    def log_to_csv(self, dir=None, filename="llmlog.csv", **kwargs):
        dir = dir or self.logger_.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.logger_.to_csv(dir=dir, filename=filename, **kwargs)
    
    async def call_chatcompletion(self, schema=oai_schema['chat'], **kwargs):
        payload = ChatCompletion.create_payload(messages=self.conversation.messages, schema=schema, llmconfig=self.llmconfig,**kwargs)
        completion = await self.service.serve(payload=payload)
        if "choices" in completion:
            self.logger_({"input":payload, "output": completion})
            self.conversation.add_messages(response=completion['choices'][0])
            self.conversation.responses.append(self.conversation.messages[-1])
            self.conversation.response_counts += 1
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1