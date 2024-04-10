# from ..configs import oai_schema

# class BaseIntelligentModel:

#     def __init__(
#         self, 
#         provider=None,
#         default_config=oai_schema['chat.py']['config'],
#         **kwargs
#     ) -> None:
#     # kwargs are the individual parameters that the model can take
#     # different for different models
#         self.provider=provider,
#         self.config = {**default_config, **kwargs},

#     async def __call__(
#         self, 
#         payload, 
#         provider=None,
#         endpoint_='chat.py/completions',
#         method='post'
#     ):
#         provider = provider or self.provider
#         return await provider.serve(
#             payload=payload, endpoint_=endpoint_, method=method
#         )

#     def set_service(self, provider):
#         self.provider = provider

#     def set_config(self, config):
#         self.config=config

#     def change_model(self, model):
#         self.config['model'] = model

#     def change_temperature(self, temperature):
#         self.config['temperature'] = temperature

#     def revert_to_default_config(self):
#         self.config = oai_schema['chat.py']['config']

#     def modify_config(self, **kwargs):
#         self.config = {**self.config, **kwargs}


# class IModel(BaseIntelligentModel):

#     def __init__(
#         self, provider=None, default_model_kwargs=None, **kwargs
#     ) -> None:
#         super().__init__(provider, default_model_kwargs, **kwargs)
