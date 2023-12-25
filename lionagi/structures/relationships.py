from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List, Union


class ConditionalRelationship(BaseModel):
    """
    Represents a conditional relationship between two nodes in a graph.

    Attributes:
        target_node_id (str): Identifier of the target node.
        properties (Dict[str, Any]): Properties associated with the relationship.
        condition (Optional[str]): Condition that must be satisfied for the relationship to take effect.
    """
    label: Optional[str] = None
    target_node_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[str] = None

    def check_condition(self, context: Dict[str, Any]) -> bool:
        """
        Check if the condition is satisfied based on the provided context.

        Args:
            context (Dict[str, Any]): Context to evaluate the condition against.

        Returns:
            bool: `True` if condition is satisfied, `False` otherwise.
        """
        return context.get(self.condition, False)