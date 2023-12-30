from .chat_completion import ChatCompletion
from .embeddings import Embeddings






    















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