def create_payload(input_, config, required_, optional_, input_key, **kwargs):
    config = {**config, **kwargs}
    payload = {input_key: input_}

    for key in required_:
        payload[key] = config[key]

    for key in optional_:
        if bool(config[key]) and str(config[key]).strip().lower() != "none":
            payload[key] = config[key]

    return payload


class PayloadPackage:

    @classmethod
    def embeddings(cls, embed_str, llmconfig, schema, **kwargs):
        return create_payload(
            input_=embed_str,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="input",
            **kwargs,
        )

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
        return create_payload(
            input_=messages,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="messages",
            **kwargs,
        )

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
        return create_payload(
            input_=training_file,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="training_file",
            **kwargs,
        )
