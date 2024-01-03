import json
from typing import Any
from dotenv import load_dotenv

from .conversations import Conversation
from ..schema import DataLogger
from lionagi.objs.tool_registry import ToolManager
from ..services import OpenAIService
from lionagi.configs.oai_configs import oai_schema
from lionagi.services.chatcompletion import ChatCompletion

from lionagi.utils.call_util import lcall, alcall

load_dotenv()
OAIService = OpenAIService()


class Session:

    def __init__(self, system, dir=None, llmconfig=oai_schema['chat']['config'], service=OAIService):

        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self._logger = DataLogger(dir=dir)
        self.service = service
        self.tool_manager = ToolManager()
    
    def set_dir(self, dir):
        self._logger.dir = dir
    
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
        msg = self.conversation.messages[-1]
        try: 
            if "function call result" in json.loads(msg['content']).keys():
                return True
        except: 
            return False    

    def register_tools(self, tools, update=False, new=False, prefix=None, postfix=None):
        if not isinstance(tools, list):
            tools=[tools]
        self.tool_manager.register_tools(tools=tools, update=update, new=new, prefix=prefix, postfix=postfix)
        tools_schema = lcall(tools, lambda tool: tool.to_dict()['schema_'])
        if self.llmconfig['tools'] is None:
            self.llmconfig['tools'] = tools_schema
        else:
            self.llmconfig['tools'] += tools_schema
    
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self._call_chatcompletion(**config)
        
        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self._call_chatcompletion(**config)

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
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    def log_to_csv(self, dir=None, filename="llmlog.csv", **kwargs):
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self._logger.to_csv(dir=dir, filename=filename, **kwargs)
    
    async def _call_chatcompletion(self, schema=oai_schema['chat'], **kwargs):
        payload = ChatCompletion.create_payload(messages=self.conversation.messages, schema=schema, llmconfig=self.llmconfig,**kwargs)
        completion = await self.service.serve(payload=payload)
        if "choices" in completion:
            self._logger({"input":payload, "output": completion})
            self.conversation.add_messages(response=completion['choices'][0])
            self.conversation.responses.append(self.conversation.messages[-1])
            self.conversation.response_counts += 1
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1