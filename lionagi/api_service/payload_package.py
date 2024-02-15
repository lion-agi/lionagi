from lionagi.utils.api_util import APIUtil

class PayloadCreation:
    
    @classmethod
    def chat_completion(cls, messages, llmconfig, schema, **kwargs):
        """
        Creates a payload for the chat completion operation.

        Args:
            messages: The messages to include in the chat completion.
            llmconfig: Configuration for the language model.
            schema: The schema describing required and optional fields.
            **kwargs: Additional keyword arguments.

        Returns:
            The constructed payload.
        """
        return APIUtil._create_payload(
            input_=messages, 
            config=llmconfig, 
            required_=schema['required'], 
            optional_=schema['optional'],
            input_key="messages", 
            **kwargs)

    @classmethod
    def fine_tuning(cls, training_file, llmconfig, schema, **kwargs):
        """
        Creates a payload for the fine-tuning operation.

        Args:
            training_file: The file containing training data.
            llmconfig: Configuration for the language model.
            schema: The schema describing required and optional fields.
            **kwargs: Additional keyword arguments.

        Returns:
            The constructed payload.
        """
        return APIUtil._create_payload(
            input_=training_file, 
            config=llmconfig, 
            required_=schema['required'], 
            optional_=schema['optional'],
            input_key="training_file", 
            **kwargs)
