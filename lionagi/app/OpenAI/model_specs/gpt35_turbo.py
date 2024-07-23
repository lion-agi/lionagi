from lionagi.os.service.api.model_config import MODEL_CONFIG, ENDPOINT_CONFIG
from .config import oai_chat_schema, oai_finetune_schema


GPT35_TURBO_CHAT_COMPLETIONS = ENDPOINT_CONFIG(
    endpoint="chat/completions",
    pricing=(0.5, 1.5),
    batch_pricing=(0.25, 0.75),
    token_limit=16_385,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={'model': "gpt3.5-turbo", **oai_chat_schema['config']},
    required_params=oai_chat_schema['required_params'],
    optional_params=oai_chat_schema['optional_params'],
    input_key=oai_chat_schema['input_key']
    
)

GPT35_FINE_TUNING = ENDPOINT_CONFIG(
    endpoint="fine-tuning",
    pricing=(3, 6, 8),              # input, output, training
    batch_pricing=(1.5, 3, 8),      
    token_limit=16_385,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={'model': "gpt3.5-turbo", **oai_finetune_schema['config']},
    required_params=oai_finetune_schema['required_params'],
    optional_params=oai_finetune_schema['optional_params'],
    input_key=oai_finetune_schema['input_key']
)


GPT35_TURBO = MODEL_CONFIG(
    model="gpt-3.5-turbo",
    alias=["gpt-3.5-turbo", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106"],
    endpoint_schema={
        "chat/completions": GPT35_TURBO_CHAT_COMPLETIONS,
        "fine-tuning": GPT35_FINE_TUNING,
    }
)