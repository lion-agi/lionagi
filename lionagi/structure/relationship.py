from pydantic import Field

from lionagi.schema.base_schema import BaseNode


class Relationship(BaseNode):
    source_node_id: str
    target_node_id: str
    condition: dict = Field(default={})

    def add_condition(self, condition: dict):
        self.condition.update(condition)

    def remove_condition(self, condition_key):
        if condition_key not in self.condition.keys():
            raise KeyError(f'condition {condition_key} is not found')
        return self.condition.pop(condition_key)

    def condition_exists(self, condition_key):
        if condition_key in self.condition.keys():
            return True
        else:
            return False

    def get_condition(self, condition_key=None):
        if condition_key is None:
            return self.condition
        if self.condition_exists(condition_key=condition_key):
            return self.condition[condition_key]
        else:
            raise ValueError(f"Condition {condition_key} does not exist")
        