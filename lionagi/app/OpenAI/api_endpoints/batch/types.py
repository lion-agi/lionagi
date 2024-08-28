from typing import Literal, TypeAlias

# Role literals
RoleLiteral = Literal["system", "user", "assistant", "tool"]

# Endpoint literals
EndpointLiteral = Literal["/v1/chat/completions", "/v1/embeddings", "/v1/completions"]

# HTTP method literals
MethodLiteral = Literal["POST"]

# Completion window literals
CompletionWindowLiteral = Literal["24h"]

# Object type literals
ObjectTypeLiteral = Literal["batch", "list", "fine_tuning.job.event"]

# Batch status TypeAlias
BatchStatusType: TypeAlias = Literal[
    "validating", "queued", "running", "succeeded", "failed", "cancelled"
]

# Model name TypeAlias (extend this list as needed)
ModelNameType: TypeAlias = Literal["gpt-4o-mini", "gpt-3.5-turbo"]

# JSON-compatible types
JsonType = dict[str, "JsonType"] | list["JsonType"] | str | int | float | bool | None
