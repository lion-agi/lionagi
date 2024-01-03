from typing import Any, Dict, Union, List, Optional
import tiktoken
from lionagi.configs.oai_configs import oai_schema



class PayloadMaker:
    """
    A class for creating and handling payloads based on given inputs and schemas.

    This class is responsible for generating structured payloads that conform to specified schemas
    and encoding rules, primarily for network requests or data processing tasks.

    Attributes:
        input_ (Union[str, List[str]]):
            The initial input data for payload creation.
        schema (Dict[str, Any]):
            A dictionary defining the structure and rules for the payload.
        encoding (Any):
            The encoding method used for processing the input data.

    Methods:
        _make:
            Generates a payload based on the input data, schema, and additional parameters.
        _calculate_num_tokens:
            Determines the number of tokens required for a specific API endpoint.
        _calculate_tokens_for_encoded_input:
            Calculates the token count for encoded input data.
        _calculate_token_chat_completions:
            Computes the token count for a chat completion payload.
        _calculate_token_completions:
            Calculates the token count for a completion payload.
        _calculate_token_embeddings:
            Determines the token count for an embeddings payload.
        _calculate_token_audio:
            Calculates the token count for an audio payload.
        _calculate_token_images:
            Computes the token count for an image payload.
        _calculate_token_fine_tuning:
            Calculates the token count for a fine-tuning payload.
        _calculate_tokens_for_file_field:
            Determines the token count for a file field in the payload.
    """
    
    def __init__(self, input_: Union[str, List[str]] = None, 
                 schema: Dict[str, Any]=None, 
                 encoding_name: str="cl100k_base") -> None:
        """
        Initializes the PayloadMaker with specified input data, schema, and encoding method.

        Parameters:
            input_ (Union[str, List[str]]):
                The input data to be processed and included in the payload.
            schema (Dict[str, Any]):
                The schema dictating the structure and rules for the payload.
            encoding_name (str):
                The name of the encoding method to be used for data transformation.
        """        
        self.input_ = input_
        self.schema = schema or oai_schema['chat']
        self.encoding = tiktoken.get_encoding(encoding_name)

    def make(self, input_: Optional[Union[str, List[str]]] = None,
                       schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Creates a payload based on the provided input data, schema, and additional parameters.

        Parameters:
            input_ (Optional[Union[str, List[str]]]):
                The input data; defaults to the instance's input if None.
            schema (Optional[Dict[str, Any]]):
                The schema to use; defaults to the instance's schema if None.
            **kwargs:
                Additional configuration parameters to override or extend the schema's config.

        Returns:
            Dict[str, Any]: A dictionary representing the created payload.
        """
        input_ = self.input_ if input_ is None else input_
        schema = self.schema if schema is None else schema
        config = {**schema.get('config', {}), **kwargs}
        payload = {schema["input"]: input_}
        config = config.update({**kwargs})
        

        for key in schema.get('required', []):
            payload[key] = config[key]

        for key in schema.get('optional', []):
            if key in config and config[key] not in [False, None, "None", "none"]:
                payload[key] = config[key]

        return payload

    def _calculate_num_tokens(self, endpoint_: str) -> int:
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
        payload = self.make()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        completion_tokens = max_tokens * n
        num_tokens = sum(4 + sum(len(self.encoding.encode(value)) for key, value in message.items()) -
                         (1 if "name" in message else 0) for message in payload["messages"])
        return num_tokens + 2 + completion_tokens

    def _calculate_token_completions(self) -> int:
        payload = self.make()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        return self._calculate_tokens_for_encoded_input(payload["prompt"]) + max_tokens * n

    def _calculate_token_embeddings(self) -> int:
        payload = self.make()
        return self._calculate_tokens_for_encoded_input(payload["input"])

    def _calculate_token_audio(self) -> int:
        return self._calculate_tokens_for_file_field("audio_file", self.make())

    def _calculate_token_images(self) -> int:
        return self._calculate_tokens_for_file_field("image_file", self.make())

    def _calculate_token_fine_tuning(self) -> int:
        return self._calculate_tokens_for_file_field("training_data", self.make())

    def _calculate_tokens_for_file_field(self, field_name: str, payload: Dict[str, Any]) -> int:
        file_data = payload.get(field_name)
        if isinstance(file_data, str):
            with open(file_data, 'rb') as f:
                file_data = f.read()
        elif not isinstance(file_data, bytes):
            raise TypeError(f'The "{field_name}" field must be a file path or bytes.')
        return len(self.encoding.encode(file_data))
    