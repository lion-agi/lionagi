openrouter_chat_llmconfig = {
    "model": "gpt-4-turbo-preview",
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

openrouter_chat_schema = {
    "required" : ["model", "frequency_penalty", "n", "presence_penalty", "response_format", "temperature", "top_p"],
    "optional": ["seed", "stop", "stream", "tools", "tool_choice", "user", "max_tokens"],
    "input": "messages",
    "config": openrouter_chat_llmconfig
    }

openrouter_finetune_llmconfig = {
    "model": "gpt-3.5-turbo",
    "hyperparameters": {
        "batch_size": "auto", 
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto"
    },
    "suffix": None,
    "training_file": None,
    }

openrouter_finetune_schema = {
    "required" : ["model", "training_file"],
    "optional": ["hyperparameters", "suffix", "validate_file"],
    "input": ["training_file"],
    "config": openrouter_finetune_llmconfig
}


openrouter_schema = {

    "chat/completions": openrouter_chat_schema,
    "finetune": openrouter_finetune_schema
    
}