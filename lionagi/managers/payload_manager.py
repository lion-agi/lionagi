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
