import json
import uuid
from typing import Any, Dict, Optional, Union, TypeVar, Type

from pydantic import BaseModel, Field, validator

# Define the type variable for BaseNode
T = TypeVar('T', bound='BaseNode')

class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="node_id")
    content: Union[str, Dict[str, Any], None, Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True
        json_encoders = {
            # Custom encoders for specific types can be placed here
        }
        
    @validator('*', pre=True, each_item=False)
    def non_empty(cls, v):
        if isinstance(v, (str, list, dict)) and len(v) == 0:
            raise ValueError("Field must not be empty")
        return v


    # json / dict
    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(by_alias=True, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        return cls(**data)


    # setters 
    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_

    def set_content(self, content: Union[str, Dict[str, Any], None, Any]) -> None:
        self.content = content
    
    def set_id(self, id_: str) -> None:
        self.id_ = id_
    
    
    # getters
    def get_meta(self) -> Dict[str, Any]:
        return self.metadata

    def get_content(self) -> Union[str, Dict[str, Any], None, Any]:
        return self.content

    def get_id(self) -> str:
        return self.id_

    # update
    def update_meta(self, **kwargs) -> None:
        self.metadata.update(kwargs)
        
        
        
        

# checked --------------------------------------------------------
class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    content: Union[str, Dict[str, Any], None, Any] = None
    metadata: Union[Dict[str, Any], None] = Field(default_factory=dict)
    label: Optional[str] = None


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        return cls(**data)


    
    def set_meta(self, metadata_: dict) -> None:
        self.metadata = metadata_
    
    def set_content(self, content: Union[str, Dict[str, Any], None, Any]):
        self.content = content

    def set_id(self, id: str):
        self.id_ = id

    def get_meta(self):
        return self.metadata
    
    def get_content(self):
        return self.content
    
    def get_id(self):
        return self.id_




class BaseTool(BaseNode):
    name: str = None
    func: Callable = None
    content: Any = None
    parser: Callable = None
    
    def initialize(self):
        ...

    def execute(self):
        ...

    def shutdown(self):
        ...

    def __enter__(self):
        self.initialize()
        return self





from typing import Dict, Any, Union, List, Optional, Callable, Tuple
import tiktoken
import json
import asyncio

class PayloadManager:
    def __init__(self, input_: Union[str, List[str]], schema: Dict[str, Any], encoding_name: str) -> None:
        self.input_ = input_
        self.schema = schema
        self.encoding = tiktoken.get_encoding(encoding_name)

    def create_payload(self, input_: Optional[Union[str, List[str]]] = None,
                       schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        input_ = self.input_ if input_ is None else input_
        schema = self.schema if schema is None else schema
        config = {**schema.get('config', {}), **kwargs}
        payload = {schema["input"]: input_}

        for key in schema.get('required', []):
            payload[key] = config[key]

        for key in schema.get('optional', []):
            if key in config and config[key] not in [False, None, "None", "none"]:
                payload[key] = config[key]

        return payload

    def calculate_num_tokens(self, endpoint_: str) -> int:
        method_name = f"_calculate_token_{endpoint_.replace('/', '_').replace('-', '_')}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f'API endpoint "{endpoint_}" not implemented.')
        return method()

    def _calculate_tokens_for_encoded_input(self, input_: Union[str, List[str], bytes]) -> int:
        if isinstance(input_, (str, bytes)):
            return len(self.encoding.encode(input_))
        elif isinstance(input_, list) and all(isinstance(i, str) for i in input_):
            return sum(len(self.encoding.encode(i)) for i in input_)
        else:
            raise TypeError('Input must be a string, bytes, or list of strings.')

    def _calculate_token_chat_completions(self) -> int:
        payload = self.create_payload()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        completion_tokens = max_tokens * n
        num_tokens = sum(4 + sum(len(self.encoding.encode(value)) for key, value in message.items()) -
                         (1 if "name" in message else 0) for message in payload["messages"])
        return num_tokens + 2 + completion_tokens

    def _calculate_token_completions(self) -> int:
        payload = self.create_payload()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        return self._calculate_tokens_for_encoded_input(payload["prompt"]) + max_tokens * n

    def _calculate_token_embeddings(self) -> int:
        payload = self.create_payload()
        return self._calculate_tokens_for_encoded_input(payload["input"])

    def _calculate_token_audio(self) -> int:
        return self._calculate_tokens_for_file_field("audio_file", self.create_payload())

    def _calculate_token_images(self) -> int:
        return self._calculate_tokens_for_file_field("image_file", self.create_payload())

    def _calculate_token_fine_tuning(self) -> int:
        return self._calculate_tokens_for_file_field("training_data", self.create_payload())

    def _calculate_tokens_for_file_field(self, field_name: str, payload: Dict[str, Any]) -> int:
        file_data = payload.get(field_name)
        if isinstance(file_data, str):
            with open(file_data, 'rb') as f:
                file_data = f.read()
        elif not isinstance(file_data, bytes):
            raise TypeError(f'The "{field_name}" field must be a file path or bytes.')
        return len(self.encoding.encode(file_data))


class ToolManager:
    def __init__(self):
        self.registry: Dict[str, BaseTool] = {}

    def _name_exists(self, name: str) -> bool:
        return name in self.registry

    def _register_tool(self, tool: BaseTool, name: Optional[str] = None, update: bool = False,
                       new: bool = False, prefix: Optional[str] = None, postfix: Optional[int] = None):
        name = name or tool.func.__name__
        original_name = name

        if self._name_exists(name):
            if update and new:
                raise ValueError("Cannot both update and create new registry for existing function.")
            if new:
                idx = 1
                while self._name_exists(f"{prefix or ''}{name}{postfix or ''}{idx}"):
                    idx += 1
                name = f"{prefix or ''}{name}{postfix or ''}{idx}"
            else:
                self.registry.pop(original_name, None)

        self.registry[name] = tool

    async def invoke(self, name: str, kwargs: Dict) -> Any:
        if not self._name_exists(name):
            raise ValueError(f"Function {name} is not registered.")

        tool = self.registry[name]
        func = tool.func
        parser = tool.parser

        try:
            result = await func(**kwargs) if asyncio.iscoroutinefunction(func) else func(**kwargs)
            return await parser(result) if parser and asyncio.iscoroutinefunction(parser) else parser(result) if parser else result
        except Exception as e:
            raise ValueError(f"Error invoking function {name}: {str(e)}")

    @staticmethod
    def parse_function_call(response: str) -> Tuple[str, Dict]:
        out = json.loads(response)
        func = out.get('function', '').lstrip('call_')
        args = json.loads(out.get('arguments', '{}'))
        return func, args

    def register_tools(self, tools: List[BaseTool], update: bool = False, new: bool = False,
                       prefix: Optional[str] = None, postfix: Optional[int] = None):
        for tool in tools:
            self._register_tool(tool, update=update, new=new, prefix=prefix, postfix=postfix)