from pydantic import BaseModel, Field
from ._default import DEFAULT_RULES, Rule


rules_ = {
    "choice": DEFAULT_RULES.CHOICE.value,
    "actionrequest": DEFAULT_RULES.ACTION_REQUEST.value,
    "bool": DEFAULT_RULES.BOOL.value,
    "number": DEFAULT_RULES.NUMBER.value,
    "dict": DEFAULT_RULES.DICT.value,
    "str": DEFAULT_RULES.STR.value,
}

order_ = [
    "choice",
    "actionrequest",
    "bool",
    "number",
    "dict",
    "str",
]


class Validator:
    """
    rules contain all rules that this validator can apply to data
    the order determines which rule gets applied in what sequence.
    notice, if a rule is not present in the orders, it will not be applied.
    """

    rules: dict[str, Rule] = Field(
        default=rules_,
        description="The rules to be used for validation.",
    )

    order: list[str] = Field(
        default=order_,
        description="The order in which the rules should be applied.",
    )

    async def validate(self, value, *args, strict=False, **kwargs):

        for i in self.order:
            if i in self.rules:
                try:
                    if (
                        a := await self.rules[i].validate(value, *args, **kwargs)
                        is not None
                    ):
                        return a
                except Exception as e:
                    raise ValueError(f"failed to validate field") from e
        if strict:
            raise ValueError(f"failed to validate field")

        return value

 

import asyncio
from typing import Dict, Tuple, Optional

class Validator:
    """Validator handles input validation and directs the scheduler based on the data received."""
    
    def __init__(self):
        # Initialize any necessary components, like database connections or external services
        pass

    async def handle_input(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Handles incoming data, validates it, and determines what action should be taken.
        
        Args:
            data (Dict): The incoming task data.

        Returns:
            Tuple[bool, Optional[str]]: A tuple containing a boolean indicating if the data is valid,
                                        and an optional string indicating the action to be taken 
                                        ('create', 'update', 'reject', or None if no specific action).
        """
        if not await self.validate(data):
            return False, None
        action = self.determine_action(data)
        return True, action

    async def validate(self, data: Dict) -> bool:
        """
        Validates the incoming data against predefined rules and requirements.
        
        Args:
            data (Dict): The incoming task data.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
        required_fields = ['report_id', 'form_id', 'data']
        if not all(field in data for field in required_fields):
            print(f"Validation failed: missing one of the required fields in {data}")
            return False
        if not isinstance(data['data'], dict):  # Expecting 'data' to be a dictionary
            print(f"Validation failed: 'data' field is not a dictionary")
            return False
        # Add additional validation checks as needed
        return True

    def determine_action(self, data: Dict) -> Optional[str]:
        """
        Determines what action should be taken based on the validated data.
        
        Args:
            data (Dict): The validated task data.

        Returns:
            Optional[str]: The action to be taken ('create', 'update', or 'reject').
        """
        # Placeholder logic to determine the action based on data contents
        if 'new' in data:
            return 'create'
        elif 'update' in data:
            return 'update'
        else:
            return 'reject'



# class Worker:
#     def __init__(self):
#         self.reports = {}
#         self.forms = {}
#         self.validator = Validator()

#     async def execute_work_function(self, function, inputs):
#         # Run the work function with the given inputs
#         output = await function(**inputs)
#         work_object = Work(data=output, status='Completed')

#         # Validate the output and decide on form handling
#         form = self.get_or_create_form(function, inputs)
#         if await self.validator.validate(output):
#             form.fill(output)
#             report = self.get_or_create_report(form)
#             report.update(form)

#         return work_object

#     def get_or_create_form(self, function, inputs):
#         # Assuming function.__name__ gives us the unique identifier for form type
#         form_type = function.__name__
#         if form_type not in self.forms:
#             self.forms[form_type] = Form()  # Or however forms are specified or initialized
#         return self.forms[form_type]

#     def get_or_create_report(self, form):
#         # Use some unique key or identifier from the form to fetch or create a new report
#         report_id = form.unique_identifier  # This needs to be defined based on your application's logic
#         if report_id not in self.reports:
#             self.reports[report_id] = Report()
#         return self.reports[report_id]

# # Example Work Function
# async def process_data(instruction, context):
#     # Simulate data processing
#     return {'result': f"Processed {instruction} with {context}"}
