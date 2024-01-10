import json
from typing import Any
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool
from lionagi.utils import lcall, alcall
from lionagi.services import OpenAIService
from lionagi.endpoints import ChatCompletion
from lionagi.objs.tool_manager import ToolManager
from lionagi.configs.oai_configs import oai_schema
from lionagi.core.conversations.conversation import Conversation

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
                # func, args = self.tool_manager._get_function_call(self.conversation.responses[-1]['content'])
                # outs = await self.tool_manager.invoke(func, args)
                # self.conversation.add_messages(response=outs)

                tool_uses = json.loads(self.conversation.responses[-1].message_content)
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
            return self.conversation.responses[-1].message_content
    
    def _is_invoked(self):
        content = self.conversation.messages[-1].message_content
        try:
            if json.loads(content).keys() >= {'function', 'arguments', 'output'}:
                return True
        except: 
            return False    

    def register_tools(self, tools): #, update=False, new=False, prefix=None, postfix=None):
        if not isinstance(tools, list):
            tools=[tools]
        self.tool_manager.register_tools(tools=tools) #, update=update, new=new, prefix=prefix, postfix=postfix)
        # tools_schema = lcall(tools, lambda tool: tool.to_dict()['schema_'])
        # if self.llmconfig['tools'] is None:
        #     self.llmconfig['tools'] = tools_schema
        # else:
        #     self.llmconfig['tools'] += tools_schema

    def _tool_parser(self, **kwargs):
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
        # if self.tool_manager.registry != {}:
        #     if 'tools' not in kwargs:
        #         tool_kwarg = {"tools": self.tool_manager.to_tool_schema_list()}
        #         kwargs = {**tool_kwarg, **kwargs}
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
        # if self.tool_manager.registry != {}:
        #     if 'tools' not in kwargs:
        #         tool_kwarg = {"tools": self.tool_manager.to_tool_schema_list()}
        #         kwargs = {**tool_kwarg, **kwargs}
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruct, num=3, **kwargs):
        # if self.tool_manager.registry != {}:
        #     if 'tools' not in kwargs:
        #         tool_kwarg = {"tools": self.tool_manager.to_tool_schema_list()}
        #         kwargs = {**tool_kwarg, **kwargs}
        if self.tool_manager.registry != {}:
            kwargs = self._tool_parser(**kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct, tool_choice="auto", tool_parsed=True, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs, tool_parsed=True)

    # def messages_to_csv(self, dir=None, filename="messages.csv", **kwargs):
    #     dir = dir or self.logger_.dir
    #     if dir is None:
    #         raise ValueError("No directory specified.")
    #     self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    # def log_to_csv(self, dir=None, filename="llmlog.csv", **kwargs):
    #     dir = dir or self.logger_.dir
    #     if dir is None:
    #         raise ValueError("No directory specified.")
    #     self.logger_.to_csv(dir=dir, filename=filename, **kwargs)
    
    async def call_chatcompletion(self, schema=oai_schema['chat'], **kwargs):
        messages = [message.message for message in self.conversation.messages]
        payload = ChatCompletion.create_payload(messages=messages, schema=schema, llmconfig=self.llmconfig,**kwargs)
        completion = await self.service.serve(payload=payload)
        if "choices" in completion:
            self.logger_({"input":payload, "output": completion})
            self.conversation.add_messages(response=completion['choices'][0])
            self.conversation.responses.append(self.conversation.messages[-1])
            self.conversation.response_counts += 1
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1
            
