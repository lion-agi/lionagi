API_key_schema = ("OPENROUTER_API_KEY",)

openrouter_chat_llmconfig = {
    "model": "gpt-4o",
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

openrouter_chat_schema = {
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
    "config": openrouter_chat_llmconfig,
    "token_encoding_name": "cl100k_base",
    "token_limit": 128_000,
    "interval_tokens": 10_000,
    "interval_requests": 100,
    "interval": 60,
}

openrouter_finetune_llmconfig = {
    "model": "gpt-3.5-turbo",
    "hyperparameters": {
        "batch_size": "auto",
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto",
    },
    "suffix": None,
    "training_file": None,
}

openrouter_finetune_schema = {
    "required": ["model", "training_file"],
    "optional": ["hyperparameters", "suffix", "validate_file"],
    "input_": ["training_file"],
    "config": openrouter_finetune_llmconfig,
}

openrouter_schema = {
    "chat/completions": openrouter_chat_schema,
    "finetune": openrouter_finetune_schema,
    "API_key_schema": API_key_schema,
}
