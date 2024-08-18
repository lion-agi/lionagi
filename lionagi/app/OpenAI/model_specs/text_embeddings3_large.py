from lionagi.os.service.schema import EndpointSchema, ModelConfig
from lionagi.app.OpenAI.model_specs._config import oai_embeddings_schema


TEXT_EMBEDDINGS3_LARGE_EMBED = EndpointSchema(
    endpoint="embeddings",
    pricing=0.13,  # input
    batch_pricing=0.065,
    token_limit=8_192,
    default_rate_limit=(60, 10_000, 5_000_000, 1, 1_000),
    default_config={
        "model": "text-embeddings-3-small",
        **oai_embeddings_schema["config"],
    },
    required_params=oai_embeddings_schema["required_params"],
    optional_params=oai_embeddings_schema["optional_params"],
    input_key=oai_embeddings_schema["input_key"],
)


TEXT_EMBEDDINGS3_LARGE_MODEL_CONFIG = ModelConfig(
    model="text-embeddings-3-large",
    alias=["text-embeddings-3-large"],
    endpoint_schema={
        "embeddings": TEXT_EMBEDDINGS3_LARGE_EMBED,
    },
)


__all__ = ["TEXT_EMBEDDINGS3_LARGE_MODEL_CONFIG"]
