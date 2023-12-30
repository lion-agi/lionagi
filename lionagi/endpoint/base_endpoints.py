import abc
from typing import Dict

async def serve_endpoint(input_, endpoint, schema, service, method="post", **kwargs):
    payload = endpoint.create_payload(input_=input_, schema=schema, **kwargs)
    return await service.serve(payload=payload, endpoint_=schema['endpoint'], method=method)



class BaseEndpoint(abc.ABC):
    
    def __init__(self)
    
    
    
    llmconfig : Dict
    
    
    
    
    
    endpoint: str = abc.abstractproperty()

    def create_payload(self):
        ...

    def process_response(self):
        ...

    @classmethod

        
class ChatCompletion(BaseEndpoint):
    endpoint: str = "chat/completion"

    @classmethod
    def create_payload(scls, input_, llmconfig, schema, **kwargs):
        payload = {"messages": input_}
        scls._create_payload(input_=payload, llmconfig=llmconfig, schema=schema, **kwargs)
        

class 






