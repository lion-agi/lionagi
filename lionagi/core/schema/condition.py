from abc import ABC, abstractmethod
from enum import Enum


class SourceType(str, Enum):
    STRUCTURE = "structure"
    EXECUTABLE = "executable"


class Condition(ABC):
    def __init__(self, source_type):
        try:
            if isinstance(source_type, str):
                source_type = SourceType(source_type)
            if isinstance(source_type, SourceType):
                self.source_type = source_type
        except:
            raise ValueError(
                f"Invalid source_type. Valid source types are {list(SourceType)}"
            )

    @abstractmethod
    def __call__(self, source_obj):
        pass
