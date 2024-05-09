# https://api.openai.com/v1/fine_tuning/jobs

# Finetune -- create fine-tuning job

oai_create_finetune_llmconfig = {
    "model": "gpt-3.5-turbo",
    "hyperparameters": None,
}

oai_create_finetune_schema = {
    "required": ["model", "training_file"],
    "optional": [
        "hyperparameters", 
        "suffix", 
        "validation_file",
        "integrations", 
        "seed"
    ],
    "input_": "training_file",
    "config": oai_create_finetune_llmconfig,
}
