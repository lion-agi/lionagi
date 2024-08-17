from lionagi.os.service.schema import EndpointSchema, ModelConfig
from lionagi.app.OpenAI.model_specs._config import oai_chat_schema


GPT4O_IMAGE_PRICING = {
    "base_cost": 85,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "square_size": 512,
    "square_cost": 170,
}


GPT4O_CHAT_COMPLETIONS = EndpointSchema(
    endpoint="chat/completions",
    pricing=(2.5, 10),  # input_token, output_token
    batch_pricing=(1.25, 5),  # input_token, output_token
    token_limit=128_000,
    default_rate_limit=(60, 1_000, 5_000_000),
    default_config={"model": "gpt-4o-2024-08-06", **oai_chat_schema["config"]},
    required_params=oai_chat_schema["required_params"],
    optional_params=oai_chat_schema["optional_params"],
    input_key=oai_chat_schema["input_key"],
    image_pricing=GPT4O_IMAGE_PRICING,
)

GPT4O_MODEL_CONFIG = ModelConfig(
    model="gpt-4o-2024-08-06",
    alias=["gpt-4o", "gpt-4o-2024-05-13"],
    endpoint_schema={
        "chat/completions": GPT4O_CHAT_COMPLETIONS,
    },
)
