from lionagi.os.service.schema import EndpointSchema, ModelConfig
from lionagi.app.OpenAI.model_specs._config import oai_chat_schema

GPT4_TURBO_CHAT_COMPLETIONS = EndpointSchema(
    endpoint="chat/completions",
    pricing=(10, 30),
    token_limit=128_000,
    default_rate_limit=(None, None, None, None, None),
    default_config={"model": "gpt-4-turbo", **oai_chat_schema["config"]},
    required_params=oai_chat_schema["required_params"],
    optional_params=oai_chat_schema["optional_params"],
    input_key=oai_chat_schema["input_key"],
)


GPT4_TURBO_MODEL_CONFIG = ModelConfig(
    model="gpt-4-turbo",
    alias=["gpt-4-turbo-2024-04-09"],
    endpoint_schema={
        "chat/completions": GPT4_TURBO_CHAT_COMPLETIONS,
    },
)


__all__ = ["GPT4_TURBO_MODEL_CONFIG"]
