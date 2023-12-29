from .base_endpoints import BaseEndpoint


class ChatCompletion(BaseEndpoint):
    endpoint: str = "chat/completion"

    @classmethod
    def create_payload(scls, input_, llmconfig, schema, **kwargs):
        payload = {"messages": input_}
        scls._create_payload(input_=payload, llmconfig=llmconfig, schema=schema, **kwargs)
