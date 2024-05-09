from typing import Type
from pydantic import Field
from lionagi.libs.ln_api import BaseService, EndPoint


from .config.chat import chat_schema


def set_up_endpoints(endpoints: EndPoint | str | dict, endpoints_config: dict = {}) -> dict[str, EndPoint]:
    if isinstance(endpoints, EndPoint):
        return {endpoints.endpoints: endpoints}
    elif isinstance(endpoints, str):
        return {endpoints: EndPoint(endpoints, **endpoints_config)}
    elif (
        isinstance(endpoints, dict) 
        and endpoints.values()[0] is EndPoint 
        and endpoints.values()[0].endpoints == endpoints.keys()[0]
    ):
        return endpoints
        
def setup_service(
    service: BaseService=None, 
    service_config: dict={}, 
    endpoints: dict[str, EndPoint] = None, 
    default_service: Type[BaseService] = None
):
    if not service:
        if default_service:
            return default_service(**service_config, endpoints=endpoints)
        else:
            from lionagi.integrations.provider.services import Services
            return Services.OpenAI(**service_config, endpoints=endpoints)
    elif isinstance(service, BaseService):
        return service
    else:
        raise ValueError("Invalid service")
        
    
class OpenAI:
    
    def __init__(
        self,
        service: BaseService=None, 
        service_config: dict={},
        endpoints: str | dict | EndPoint="chat/completions",      # endpoints obj or str like "chat/completions"
        endpoints_config: dict={},
        llmconfig: dict={},
        schema:dict=chat_schema,
        **kwargs
    ) -> None:
        
        endpoints = set_up_endpoints(endpoints, endpoints_config)
        
        from lionagi.integrations.provider.oai import OpenAIService
        self.service = setup_service(service, service_config, endpoints, default_service=OpenAIService)    
        self.config = {**llmconfig, **kwargs}
        self.schema = schema


    async def predict(self, messages, **kwargs):
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        return payload, completion

