from .base_model import BaseIntelligentModel

class IModel(BaseIntelligentModel):
    
    def __init__(
        self, service=None, default_model_kwargs=None, **kwargs
    ) -> None:
        super().__init__(service, default_model_kwargs, **kwargs)
        