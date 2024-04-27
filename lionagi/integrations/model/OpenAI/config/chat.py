# https://api.openai.com/v1/chat/completions


chat_llmconfig = {
    "model": "gpt-4-turbo",
    "frequency_penalty": 0,
    "logit_bias": None,
    "logprobs": False, 
    "top_logprobs": None,
    "max_tokens": None, 
    "n": 1,
    "presence_penalty": 0,
    "response_format": {"type": "text"},
    "seed": None,
    "stop": None,
    "stream": False,
    "temperature": 1,
    "top_p": 1,
    "tools": None, 
    "tool_choice": "none",
    "user": None,
    "max_tokens": None,
}


chat_schema = {
    "required": [
        "model",
        "frequency_penalty",
        "n",
        "presence_penalty",
        "response_format",
        "temperature",
        "top_p",
    ],
    "optional": [
        "logit_bias",
        "logprobs",
        "top_logprobs",
        "seed",
        "stop",
        "stream",
        "tools",
        "tool_choice",
        "user",
        "max_tokens",
    ],
    "input_": "messages",
    "config": chat_llmconfig,
}
