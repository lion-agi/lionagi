from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict, Any

from .base_component import BaseComponent


class SourceType(str, Enum):
    """
    Enumeration for specifying the type of source.
    """

    STRUCTURE = "structure"
    EXECUTABLE = "executable"


class Condition(ABC):
    """
    Defines an abstract base class for conditions associated with relationships.

    This class is intended to be subclassed to create specific types of conditions that
    can be evaluated against given objects.

    Attributes:
        source_type (SourceType): The type of source the condition is associated with.
    """

    def __init__(self, source_type: SourceType | str) -> None:
        """
        Initializes a Condition with a source type.

        Args:
            source_type (SourceType | str): The type of source.

        Raises:
            ValueError: If `source_type` is not a valid `SourceType`.
        """
        try:
            if isinstance(source_type, str):
                source_type = SourceType(source_type)
            if isinstance(source_type, SourceType):
                self.source_type = source_type
        except Exception as e:
            raise ValueError(
                f"Invalid source_type. Valid source types are {list(SourceType)}"
            ) from e

    @abstractmethod
    def __call__(self, source_obj):
        """
        Evaluates the condition against a source object.

        Args:
            source_obj (Any): The object to evaluate the condition against.

        Returns:
            bool: The result of the condition evaluation.
        """
        pass


class Edge(BaseComponent):

    source_node_id: str
    target_node_id: str
    bundle: bool = False
    condition: Callable = None

    def add_condition(self, condition: Condition) -> None:

        if not isinstance(condition, Condition):
            raise ValueError(
                "Invalid condition type, please use Condition class to build a valid condition"
            )
        self.condition = condition

    def check_condition(self, source_obj: Any) -> bool:

        try:
            return bool(self.condition(source_obj))
        except Exception as e:
            raise ValueError("Invalid edge condition function") from e

    def _source_existed(self, obj: Dict[str, Any]) -> bool:

        return self.source_node_id in obj.keys()

    def _target_existed(self, obj: Dict[str, Any]) -> bool:

        return self.target_node_id in obj.keys()

    def _is_in(self, obj: Dict[str, Any]) -> bool:

        if self._source_existed(obj) and self._target_existed(obj):
            return True

        elif self._source_existed(obj):
            raise ValueError(f"Target node {self.source_node_id} does not exist")
        else:
            raise ValueError(f"Source node {self.target_node_id} does not exist")

    def __str__(self) -> str:
        """
        Returns a simple string representation of the Relationship.
        """

        return (
            f"Edge (id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"label={self.label})"
        )

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Relationship.

        Examples:
            >>> edge = Relationship(source_node_id="node1", target_node_id="node2")
            >>> repr(edge)
            'Relationship(id_=None, from=node1, to=node2, content=None, metadata=None, label=None)'
        """
        return (
            f"Edge(id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"content={self.content}, metadata={self.metadata}, label={self.label})"
        )
