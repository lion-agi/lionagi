from lionagi.os.service.api.model_config import MODEL_CONFIG, ENDPOINT_CONFIG
from .config import oai_embeddings_schema


TEXT_EMBEDDINGS3_SMALL_EMBED = ENDPOINT_CONFIG(
    endpoint="embed",
    pricing=0.02,
    batch_pricing=0.01,
    token_limit=8_192,
    default_rate_limit=(60, 3_000, 5_000_000),
    default_config={
        "model": "text-embeddings-3-small",
        **oai_embeddings_schema["config"],
    },
    required_params=oai_embeddings_schema["required_params"],
    optional_params=oai_embeddings_schema["optional_params"],
    input_key=oai_embeddings_schema["input_key"],
)


TEXT_EMBEDDINGS3_SMALL = MODEL_CONFIG(
    model="text-embeddings-3-small",
    alias=["text-embeddings-3-small"],
    endpoint_schema={
        "embeddings": TEXT_EMBEDDINGS3_SMALL_EMBED,
    },
)
