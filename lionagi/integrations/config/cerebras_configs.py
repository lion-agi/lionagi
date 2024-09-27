# Default configs for the Cerebras API

API_key_schema = ("CEREBRAS_API_KEY",)

cerebras_chat_llmconfig = {
    "model": "llama3.1-70b",
    "frequency_penalty": 0,
    "max_tokens": None,
    "num": 1,
    "presence_penalty": 0,
    "response_format": {"type": "text"},
    "seed": None,
    "stop": None,
    "stream": False,
    "temperature": 0.1,
    "top_p": 1,
    "tools": None,
    "tool_choice": "none",
    "user": None,
    "logprobs": False,
    "top_logprobs": None,
}

cerebras_chat_schema = {
    "required": [
        "model",
        "frequency_penalty",
        "num",
        "presence_penalty",
        "response_format",
        "temperature",
        "top_p",
    ],
    "optional": [
        "seed",
        "stop",
        "stream",
        "tools",
        "tool_choice",
        "user",
        "max_tokens",
        "logprobs",
        "top_logprobs",
    ],
    "input_": "messages",
    "config": cerebras_chat_llmconfig,
    "token_encoding_name": "cl100k_base",
    "token_limit": 128_000,
    "interval_tokens": 10_000,
    "interval_requests": 100,
    "interval": 60,
}

cerebras_finetune_llmconfig = {
    "model": "llama3.1-8b",
    "hyperparameters": {
        "batch_size": "auto",
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto",
    },
    "suffix": None,
    "training_file": None,
}

cerebras_finetune_schema = {
    "required": ["model", "training_file"],
    "optional": ["hyperparameters", "suffix", "validate_file"],
    "input_": ["training_file"],
    "config": cerebras_finetune_llmconfig,
}

cerebras_schema = {
    "chat/completions": cerebras_chat_schema,
    "finetune": cerebras_finetune_schema,
    "API_key_schema": API_key_schema,
}
