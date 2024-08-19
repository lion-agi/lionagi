from lionagi.os.service.schema import EndpointSchema, ModelConfig
from lionagi.app.OpenAI.model_specs._config import oai_chat_schema, oai_finetune_schema


GPT4O_MINI_IMAGE_PRICING = {
    "base_cost": 2833,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "square_size": 512,
    "square_cost": 5667,
}

GPT4O_MINI_CHAT_COMPLETIONS = EndpointSchema(
    endpoint="chat/completions",
    pricing=(0.15, 0.6),
    batch_pricing=(0.075, 0.3),
    token_limit=128_000,
    default_rate_limit=(None, None, None, None, None),
    default_config={"model": "gpt-4o-mini", **oai_chat_schema["config"]},
    required_params=oai_chat_schema["required_params"],
    optional_params=oai_chat_schema["optional_params"],
    input_key=oai_chat_schema["input_key"],
    image_pricing=GPT4O_MINI_IMAGE_PRICING,
)


GPT4O_MINI_FINETUNE = EndpointSchema(
    endpoint="finetune",
    pricing=(0.3, 1.2, 3),
    batch_pricing=(0.15, 0.6, 3),
    token_limit=128_000,
    default_rate_limit=(None, None, None, None, None),
    default_config={"model": "gpt-4o-mini", **oai_finetune_schema["config"]},
    required_params=oai_finetune_schema["required_params"],
    optional_params=oai_finetune_schema["optional_params"],
    input_key=oai_finetune_schema["input_key"],
)

GPT4O_MINI_MODEL_CONFIG = ModelConfig(
    model="gpt-4o-mini",
    alias=["gpt-4o-mini-2024-07-18", "gpt-4o-mini"],
    endpoint_schema={
        "chat/completions": GPT4O_MINI_CHAT_COMPLETIONS,
        "fine-tuning": GPT4O_MINI_FINETUNE,
    },
)


__all__ = ["GPT4O_MINI_MODEL_CONFIG"]
