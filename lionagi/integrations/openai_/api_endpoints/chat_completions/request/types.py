from enum import Enum


class Detail(str, Enum):
    AUTO = "auto"
    LOW = "low"
    HIGH = "high"


class ServiceTier(str, Enum):
    AUTO = "auto"
    DEFAULT = "default"


class ToolChoice(str, Enum):
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"
