oai_schema = {
    "required" : ["model", "frequency_penalty", "n", "presence_penalty", "response_format", "temperature", "top_p"],
    "optional": ["seed", "stop", "stream", "tools", "tool_choice", "user", "max_tokens"]
    }

oai_llmconfig = {
    "model": "gpt-4-1106-preview",
    "frequency_penalty": 0,
    "max_tokens": None,
    "n": 1,
    "presence_penalty": 0, 
    "response_format": {"type": "text"}, 
    "seed": None, 
    "stop": None,
    "stream": False,
    "temperature": 0.7, 
    "top_p": 1, 
    "tools": None,
    "tool_choice": "none", 
    "user": None
    }