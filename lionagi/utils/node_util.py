import networkx as nx
import json
from pydantic import BaseModel, Field
from typing import Any, Optional, Union, Dict, str
from .sys_util import create_id, to_list


class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    label: Optional[str] = None
    content: Union[str, Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod 
    def class_name(cls):
        return cls.__name__

    def to_json(self):
        return json.dumps(dict(self))

    def to_dict(self):
        return dict(self)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseNode":
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        return cls(**data)


class ConditionalRelationship(BaseModel):
    target_node_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[str] = None

    def check_condition(self, context: Dict[str, Any]) -> bool:
        return context.get(self.condition, False)


class GraphNode(BaseNode):
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)

    class Config:
        arbitrary_types_allowed = True
    
    def add_relationship(self, target_node_id: str, relationship_type: str, properties: Optional[Dict[str, Any]] = None, condition: Optional[str] = None):
        self.graph.add_edge(self.id_, target_node_id, relationship_type=relationship_type, properties=properties or {}, condition=condition)

    def remove_relationship(self, target_node_id: str):
        if self.graph.has_edge(self.id_, target_node_id):
            self.graph.remove_edge(self.id_, target_node_id)

    def get_relationships(self):
        return to_list(self.graph.edges(self.id_, data=True))

    def get_conditional_relationships(self):
        _, target_id, data in self.graph.edges(self.id_, data=True):
            
        
        
        
        return [(target_id, data) for  if "condition" in data]








class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(uuid4()), alias="node_id")
    label: Optional[str] = None
    content: Optional[Union[str, Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)





# Example usage
node1 = BaseNode(label="StartInstruction")
node2 = BaseNode(label="NextInstruction")
node1.add_conditional_relationship(node2.id_, properties={"action": "proceed"}, condition="user_agrees")

relationships = node1.get_conditional_relationships()
print("Conditional Relationships:", relationships)






    
    
    

# Example usage
node = BaseNode(label="ExampleNode", content="Sample Content")
print(node.to_json())  # JSON representation
print(node.to_dict())  # Dictionary representation
