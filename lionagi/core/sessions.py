import json
from typing import Any
from dotenv import load_dotenv

from .conversations import Conversation
from ..schema import DataLogger
from ..tools.tool_utils import ToolManager
from ..services import OpenAIService
from ..endpoint.chat_completion import ChatCompletion
from ..endpoint.embeddings import Embeddings
from ..configs.oai_configs import oai_chat_schema, oai_finetune_schema

load_dotenv()
OAIService = OpenAIService()


class Session:

    def __init__(self, system, dir=None, schema=oai_chat_schema, service=OAIService, llmconfig=None):
        
        self.system = system
        self.conversation = Conversation()
        
        schema = schema.copy()
        self.llmconfig = {**schema['config'], **llmconfig}
        self._schema = schema.update({"config": self.llmconfig})
        self._service = service
        self._logger = DataLogger(dir=dir)
        self._toolmanager = ToolManager()
    
    def set_dir(self, dir):
        self._logger.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        self._service = service
    
    def set_schema(self, schema):
        if not schema.get('config', None):
            schema['config'] = {**self._schema['config']}                
        self._schema = schema
    
    
    # ------------------------------------------------ Tools -------------------------------------------------------   
    
    # async def _output(self, invoke=True, out=True):
    #     if invoke:
    #         try:
    #             async def _try_output():
                 
    #                 func, args = self._toolmanager._get_function_call(self.conversation.responses[-1]['content'])
    #                 outs = await self._toolmanager.invoke(func, args)
    #                 self.conversation.add_messages(response=outs)
                
                
    #         except:
    #             pass
    #     if out:
    #         return self.conversation.responses[-1]['content']
    
    # def _is_invoked(self):
    #     msg = self.conversation.messages[-1]
    #     try: 
    #         if "function call result" in json.loads(msg['content']).keys():
    #             return True
    #     except: 
    #         return False    

    # def register_tools(self, tools, update=False, new=False, prefix=None, postfix=None):
    #     if not isinstance(tools, list):
    #         tools=[tools]
    #     self._toolmanager.register_tools(tools=tools, update=update, new=new, prefix=prefix, postfix=postfix)
    
    
    # ---------------------------------------------------- Call API -------------------------------------
    
    # async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, **kwargs) -> Any:
    #     config = {**self.llmconfig, **kwargs}
    #     system = system or self.system
    #     self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
    #     await self._call_chatcompletion(**config)
        
    #     return await self._output(invoke, out)

    # async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
    #     if system:
    #         self.conversation.change_system(system)
    #     self.conversation.add_messages(instruction=instruction, context=context, name=name)
    #     config = {**self.llmconfig, **kwargs}
    #     await self._call_chatcompletion(**config)

    #     return await self._output(invoke, out)

    # async def auto_followup(self, instruct, num=3, **kwargs):
    #     cont_ = True
    #     while num > 0 and cont_ is True:
    #         await self.followup(instruct, tool_choice="auto", **kwargs)
    #         num -= 1
    #         cont_ = True if self._is_invoked() else False
    #     if num == 0:
    #         await self.followup(instruct, **kwargs)



    # ------------------------------------------------------ save data---------------------------------
    # def messages_to_csv(self, dir=None, filename="messages.csv", **kwargs):
    #     dir = dir or self._logger.dir
    #     if dir is None:
    #         raise ValueError("No directory specified.")
    #     self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    # def log_to_csv(self, dir=None, filename="llmlog.csv", **kwargs):
    #     dir = dir or self._logger.dir
    #     if dir is None:
    #         raise ValueError("No directory specified.")
    #     self._logger.to_csv(dir=dir, filename=filename, **kwargs)
    
    
    async def call_chatcompletion(self, schema=None, **kwargs):
        schema = schema or self._schema
        payload = ChatCompletion.create_payload(input_=self.conversation.messages, 
                                                schema=schema,
                                                llmconfig=self.llmconfig,**kwargs)
        completion = await self._service.serve(payload=payload)
        return completion
        
    async def call_embedding(self, input_, schema, **kwargs):
        payload = Embeddings.create_payload(input_=input_, schema=schema, **kwargs)
        completion = await self._service.serve(payload=payload, endpoint="embeddings")
        return completion
    
    
    
        
        
        
        # if "choices" in completion:
        #     self._logger({"input":payload, "output": completion})
        #     self.conversation.add_messages(response=completion['choices'][0])
        #     self.conversation.responses.append(self.conversation.messages[-1])
        #     self.conversation.response_counts += 1
        #     self._service.status_tracker.num_tasks_succeeded += 1
        # else:
        #     self._service.status_tracker.num_tasks_failed += 1
            

    
    