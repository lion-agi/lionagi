import json
import networkx as nx
from collections import deque
import operator
from typing import Any, Dict
from .utils.sys_utils import create_path, create_id
from .utils.io_util import to_csv
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable

from pydantic import BaseModel, Field, validator

T = TypeVar('T', bound='BaseNode')


class DataLogger:

    def __init__(self, dir= None, log: list = None) -> None:
        self.dir = dir
        self.log = deque(log) if log else deque()

    def __call__(self, entry):
        self.log.append(entry)

    def to_csv(self, filename: str, dir=None, verbose: bool = True, timestamp: bool = True, dir_exist_ok=True, file_exist_ok=False):
        dir = dir or self.dir
        filepath = create_path(dir=dir, filename=filename, timestamp=timestamp, dir_exist_ok=dir_exist_ok)
        to_csv(list(self.log), filepath, file_exist_ok=file_exist_ok)
        n_logs = len(list(self.log))
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            
    def set_dir(self, dir: str):
        self.dir = dir


class BaseNode(BaseModel):

    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    content: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True
        json_encoders = {
            # Custom encoders for specific types can be placed here
        }

    @validator('*', pre=True, each_item=False)
    def non_empty(cls, v):
        if isinstance(v, (str, list, dict)) and not v:
            raise ValueError("Field must not be empty")
        return v

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        return cls(**data)

    def copy(self, deep=True, n=1) -> T:
        copies = [self.model_copy(deep=deep) for i in range(n)]
        return copies[0] if n==1 else copies

    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        if not overwrite:
            other_metadata = {k: v for k, v in other_metadata.items() if k not in self.metadata}
        self.metadata.update(other_metadata)

    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_

    def get_meta(self) -> Dict[str, Any]:
        return self.metadata

    def set_content(self, content: Optional[Any]) -> None:
        self.content = content

    def get_content(self) -> Optional[Any]:
        return self.content

    def set_id(self, id_: str) -> None:
        self.id_ = id_

    def get_id(self) -> str:
        return self.id_

    def update_meta(self, **kwargs) -> None:
        self.metadata.update(kwargs)

    def add_related_node(self, node_id: str) -> None:
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)

    def remove_related_node(self, node_id: str) -> None:
        self.related_nodes = [id_ for id_ in self.related_nodes if id_ != node_id]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, T):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    def __str__(self) -> str:
        return f"BaseNode(id={self.id_}, label={self.label})"

    def __repr__(self) -> str:
        return f"BaseNode(id={self.id_}, content={self.content}, metadata={self.metadata}, label={self.label})"
    
    # Utility Methods
    def is_empty(self) -> bool:
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        return key in self.metadata


class DataNode(BaseNode):
    
    ...


class File(DataNode):

    ...
    

class Chunk(DataNode):

    ...    


class BaseTool(BaseNode):
    name: str = None
    func: Callable = None
    content: Any = None
    parser: Callable = None
    
    ...

    
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

   
class Structure(BaseNode):
    nodes: List[T] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    graph: 'nx.Graph' = nx.DiGraph()

    def add_node(self, node: T) -> None:
        self.graph.add_node(node.id_, content=node.content, metadata=node.metadata)

    def remove_node(self, node_id: str) -> None:
        self.nodes = [node for node in self.nodes if node.get_id() != node_id]
        self.relationships = [rel for rel in self.relationships if rel.target_node_id != node_id and rel.get_id() != node_id]

    def get_node(self, node_id: str) -> Optional[T]:
        return next((node for node in self.nodes if node.get_id() == node_id), None)

    def add_relationship(self, relationship: Relationship) -> None:
        if self.get_node(relationship.get_id()) and self.get_node(relationship.target_node_id):
            self.relationships.append(relationship)

    def remove_relationship(self, relationship_id: str) -> None:
        self.relationships = [rel for rel in self.relationships if rel.get_id() != relationship_id]

    def get_relationships(self, node_id: str) -> List[Relationship]:
        return [rel for rel in self.relationships if rel.get_id() == node_id or rel.target_node_id == node_id]

    def evaluate_conditions(self, context: Dict[str, Any]) -> List[Relationship]:
        return [rel for rel in self.relationships if all(rel.evaluate_condition(cond, context) for cond in rel.conditions)]

    def add_relationship(self, source_node_id: str, target_node_id: str, relationship: Relationship) -> None:
        self.graph.add_edge(source_node_id, target_node_id,
                            label=relationship.label,
                            properties=relationship.properties,
                            condition=relationship.condition)

    def remove_relationship(self, source_node_id: str, target_node_id: str) -> None:
        if self.graph.has_edge(source_node_id, target_node_id):
            self.graph.remove_edge(source_node_id, target_node_id)

    def get_relationships(self, node_id: str) -> list:
        return list(self.graph.edges(node_id, data=True))
    