from .base_endpoints import BaseEndpoint


class Embeddings(BaseEndpoint):
    endpoint: str = "embeddings"

    @classmethod
    def create_payload(scls, input_, llmconfig, schema, **kwargs):
        payload = {"input": input_}
        scls._create_payload(input_=payload, llmconfig=llmconfig, schema=schema, **kwargs)