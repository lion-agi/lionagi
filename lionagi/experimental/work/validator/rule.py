from abc import abstractmethod


class Rule:

    def __init__(self, **kwargs):
        self.validation_kwargs = kwargs
        self.fix = kwargs.get("fix", False)

    @abstractmethod
    def condition(self, **kwargs):
        pass

    @abstractmethod
    async def validate(self, value, **kwargs):
        pass
    
class Rule:
    """Base class for all validation rules."""
    
    def __init__(self, description: str):
        self.description = description  # Descriptive text to explain the rule

    async def applies(self, data: dict) -> bool:
        """
        Determines if this rule should apply to the given data set.
        
        Args:
            data (dict): The data to check applicability against.

        Returns:
            bool: True if the rule applies, False otherwise.
        """
        raise NotImplementedError("Must implement method to check applicability.")

    async def validate(self, data: dict) -> bool:
        """
        Applies the rule's logic to the data if applicable and returns the result.
        
        Args:
            data (dict): The data to validate.

        Returns:
            bool: True if the data passes the rule, False otherwise.
        """
        raise NotImplementedError("Must implement validation logic.")

    async def error_message(self) -> str:
        """Returns a custom error message if the validation fails."""
        return self.description


class RequiredFieldsRule(Rule):
    def __init__(self, fields: list, description: str = ""):
        super().__init__(description if description else f"Checks if all required fields {fields} are present.")
        self.required_fields = fields

    async def applies(self, data: dict) -> bool:
        # This rule always applies as it's a generic check
        return True

    async def validate(self, data: dict) -> bool:
        return all(field in data for field in self.required_fields)
