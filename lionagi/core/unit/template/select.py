from enum import Enum

from .base import BaseUnitForm, Field


class SelectTemplate(BaseUnitForm):
    """
    A template for performing a selection task based on given instructions and context.

    Inherits from `BaseUnitForm` and adds fields and methods specific to selection tasks.

    Attributes:
        confidence_score (float | None): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the selection.
        reason (str | None): A brief reason for the given output.
        template_name (str): The name of the template.
        selection (Enum | str | list | None): The selection from given choices.
        choices (list): The given choices to select from.
        assignment (str): A string representing the task assignment for the selection.
    """

    confidence_score: float | None = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        default_factory=str,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "default_select"

    selection: Enum | str | list | None = Field(
        None, description="selection from given choices"
    )
    choices: list = Field(
        default_factory=list, description="the given choices"
    )

    assignment: str = "task -> selection"

    @property
    def answer(self):
        """
        Gets the selection attribute.

        Returns:
            Enum | str | list | None: The selection from given choices.
        """
        return getattr(self, "selection", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        choices=None,
        reason=False,
        confidence_score=False,
        **kwargs,
    ):
        """
        Initializes a new instance of the SelectTemplate class.

        Args:
            instruction (str, optional): Additional instructions for the selection task.
            context (str, optional): Additional context for the selection task.
            choices (list, optional): The choices to select from.
            reason (bool, optional): Whether to include a reasoning field. Defaults to False.
            confidence_score (bool, optional): Whether to include a confidence score. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.choices = choices
        self.task = f"""
select 1 item from the provided choices {choices}.
1. additional objective: {instruction or "N/A"}.
2. additional information: {context or "N/A"}.
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")
