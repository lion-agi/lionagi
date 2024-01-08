# from .base_endpoint import BaseEndpoint


# class Audio(BaseEndpoint):
#     endpoint: str = "chat/completions"

#     @classmethod
#     def create_payload(scls, messages, llmconfig, schema, **kwargs):
#         config = {**llmconfig, **kwargs}
#         payload = {"messages": messages}
#         for key in schema['required']:
#             payload.update({key: config[key]})

#         for key in schema['optional']:
#             if bool(config[key]) is True and str(config[key]).lower() != "none":
#                 payload.update({key: config[key]})
#         return payload