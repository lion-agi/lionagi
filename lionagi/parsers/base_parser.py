from typing import Any

class BaseParser:
    def __init__(self, input_data: str):
        """
        Initializes the BaseParser with input data to be parsed.

        :param input_data: The raw input data as a string.
        """
        self.input_data = input_data
        self.parsed_data = None

    def validate_input(self) -> bool:
        """
        Validates the input data to ensure it meets the parser's requirements.
        Subclasses can override this method to implement specific validation logic.

        :return: True if the input data is valid, False otherwise.
        """
        # Basic validation to check if input_data is not empty
        return bool(self.input_data)

    def parse(self) -> Any:
        """
        Parses the input data into a structured format.
        This method should be implemented by subclasses.

        :return: The parsed data in a structured format.
        """
        raise NotImplementedError("Subclasses must implement the parse method.")

    def get_parsed_data(self) -> Any:
        """
        Returns the parsed data after parsing has been completed.

        :return: The parsed data in a structured format.
        """
        if self.parsed_data is None:
            if not self.validate_input():
                raise ValueError("Input data validation failed.")
            self.parsed_data = self.parse()
        return self.parsed_data
