import operator
from typing import Dict, Any, List

class Relationship:
    
    def __init__(self):
        self.target_node_id: str
        self.conditions: Dict[str, Any]
        self.linked_relationships: List[str] # Store IDs of linked relationships

    def add_condition(self, key: str, value: Any) -> None:
        self.conditions[key] = value

    def remove_condition(self, key: str) -> None:
        if key in self.conditions:
            del self.conditions[key]

    def add_conditions(self, conditions: Dict[str, Any]) -> None:
        self.conditions.update(conditions)

    def remove_conditions(self, condition_keys: List[str]) -> None:
        for key in condition_keys:
            self.conditions.pop(key, None)

    def condition_exists(self, condition_key: str) -> bool:
        return condition_key in self.conditions

    def get_condition(self, condition_key: str) -> Any:
        if not self.condition_exists(condition_key):
            raise ValueError(f"Condition {condition_key} does not exist")
        return self.conditions[condition_key]

    def evaluate_condition(self, condition_key: str, context: Dict[str, Any]) -> bool:
        if not self.condition_exists(condition_key):
            raise ValueError(f"Condition {condition_key} does not exist")

        condition = self.conditions[condition_key]

        # Example: Simple evaluation using operators
        # This can be expanded to support more complex logic
        try:
            if 'operator' in condition and 'value' in condition:
                op_func = getattr(operator, condition['operator'])
                return op_func(context.get(condition_key), condition['value'])
            else:
                raise NotImplementedError("Complex condition evaluation not yet implemented")
        except Exception as e:
            raise ValueError(f"Invalid condition format: {e}")

    def link_relationship(self, relationship_id: str) -> None:
        if relationship_id not in self.linked_relationships:
            self.linked_relationships.append(relationship_id)

    def unlink_relationship(self, relationship_id: str) -> None:
        self.linked_relationships = [id_ for id_ in self.linked_relationships if id_ != relationship_id]
