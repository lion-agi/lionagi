from re import M


class ModelService:

    @staticmethod
    def OpenAI(api_key=None, api_key_schema=None): 
        from lionagi.app.OpenAI.provider_service import OpenAIService
        return OpenAIService(api_key=api_key, api_key_schema=api_key_schema)


    @staticmethod
    def create_service(provider: str=None, api_key=None, api_key_schema=None): 
        if provider is None or provider.strip().lower() == "openai":
            return ModelService.OpenAI(api_key=api_key, api_key_schema=api_key_schema)
        
        
        ...
        
    
        
