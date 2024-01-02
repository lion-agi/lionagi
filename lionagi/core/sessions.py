import json
from typing import Any
from dotenv import load_dotenv

from lionagi.utils.type_util import to_list
from lionagi.utils.call_util import alcall, lcall
from .conversations import Conversation
from ..schema.data_logger import DataLogger
from ..objs.tool_registry import ToolRegistry
from ..services import OpenAIService


load_dotenv()
OAIService = OpenAIService()


class Session:

    def __init__(self, system, dir=None, schema=None, service=OpenAIService, llmconfig=None):
        
        self.system = system
        if schema: 
            schema = schema.copy()

        self.llmconfig = {**schema['config'], **llmconfig}
        self.schema = schema.update({"config": self.llmconfig})
        self.service = service
        self.logger = DataLogger(dir=dir)
        self.tool_registry = ToolRegistry()
        self.conversation = Conversation()
        
    
    def set_dir(self, dir):
        self.logger.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        self.service = service
    
    def set_schema(self, schema):
        if not schema.get('config', None):
            schema['config'] = {**self.schema['config']}                
        self.schema = schema
    
    async def _output(self, invoke=True, out=True):
        if invoke:
            try:
                tool_uses = json.loads(self.conversation.responses[-1]['content'])
                if 'function_list' in tool_uses.keys():
                    func_calls = await alcall(tool_uses['function_list'], self.tool_registry.get_function_call)

                else:
                    func_calls = await alcall(tool_uses['tool_uses'], self.tool_registry.get_function_call)

                outs = await alcall(func_calls, self.tool_registry.invoke)
                for out, f in zip(outs, func_calls):
                    response = {"function": f[0], "arguments": f[1], "output": out}
                    self.conversation.add_messages(response=response)
            except:
                pass
        if out:
            return self.conversation.responses[-1]['content']
    
    def _is_invoked(self):
        msg = self.conversation.api_messages[-1]
        try: 
            if "function call result" in json.loads(msg['content']).keys():
                return True
        except: 
            return False    

    def register_tools(self, tools, update=False, new=False, prefix=None, postfix=None):
        if not isinstance(tools, list):
            tools=[tools]
        self.tool_registry.register_tools(tools=to_list(tools), update=update, new=new, prefix=prefix, postfix=postfix)
    
    def register_funcs(self, funcs, parsers=None, **kwargs):
        try:
            self.tool_registry.register_funcs(funcs=funcs, parsers=parsers, **kwargs)
        except Exception as e:
            raise ValueError(f"The following error occurred while registering functions: {e}")
            
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self.call_chatcompletion(**config)
        
        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruct, num=3, **kwargs):
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct, tool_choice="auto", **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs)

    def messages_to_csv(self, dir=None, filename="messages.csv", **kwargs):
        dir = dir or self.logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msgr.to_csv(dir=dir, filename=filename, **kwargs)
        
    def log_to_csv(self, dir=None, filename="llmlog.csv", **kwargs):
        dir = dir or self.logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.logger.to_csv(dir=dir, filename=filename, **kwargs)
    
    async def call_chatcompletion(self, schema=None, **kwargs):
        schema = schema or self.schema
        completion = await self.service.serve(
            input_=self.conversation.api_messages, 
            schema=schema,
            llmconfig=self.llmconfig,
            **kwargs
            )
        return completion
        
    # async def call_embedding(self, input_, schema, **kwargs):
    #     payload = Embeddings.create_payload(input_=input_, schema=schema, **kwargs)
    #     completion = await self._service.serve(payload=payload, endpoint="embeddings")
    #     return completion
    
    #     if "choices" in completion:
    #         self._logger({"input":payload, "output": completion})
    #         self.conversation.add_messages(response=completion['choices'][0])
    #         self.conversation.responses.append(self.conversation.api_messages[-1])
    #         self.conversation.response_counts += 1
    #         self._service.status_tracker.num_tasks_succeeded += 1
    #     else:
    #         self._service.status_tracker.num_tasks_failed += 1
            