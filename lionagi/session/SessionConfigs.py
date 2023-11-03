class SessionConfig:
    """
    Manages the configuration settings for a Session object.
    
    Attributes:
        config (dict): A dictionary containing key-value pairs for default configuration settings.
    """    
    def __init__(self):
        self.config = {
            "model": "gpt-4",
            "frequency_penalty": 0,
            "n": 1,
            "stream": False,
            "temperature": 1,
            "top_p": 1,
            "sleep": 0.1,
            "out": True,
            "function_call": None,
            "functions": None,
            "stop": None
        }