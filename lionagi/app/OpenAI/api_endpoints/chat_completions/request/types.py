from typing import Literal, TypeAlias

RoleLiteral: TypeAlias = Literal["system", "user", "assistant", "tool"]
DetailLiteral: TypeAlias = Literal["auto", "low", "high"]
FormatTypeLiteral: TypeAlias = Literal["text", "json_object", "json_schema"]
ServiceTierLiteral: TypeAlias = Literal["auto", "default"]
ToolChoiceLiteral: TypeAlias = Literal["none", "auto", "required"]
