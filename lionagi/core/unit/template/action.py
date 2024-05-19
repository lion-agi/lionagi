from .base import BaseUnitForm, Field


class ActionTemplate(BaseUnitForm):

    action_required: bool | None = Field(
        None,
        description="Set to True if actions are required. Provide actions if True."
    )

    actions: list[dict] | None = Field(
        None,
        description=(
            "A list of actions to take. Format: [{'function': func, 'arguments': "
            "{'param1':..., 'param2':...}}]. Leave blank if no actions are needed."
            "must use provided functions and parameters, DO NOT MAKE UP NAMES!!!"
            "Flag `action_required` as True if filled."
        )
    )

    answer: str | None = Field(
        None,
        description=(
            "output answer to the questions asked if further actions are not needed,"
            " leave blank if an accurate answer cannot be provided from context"
            " during this step"),
    )

    assignment: str = "task -> reason, action_required, actions, answer"

    def __init__(
        self,
        instruction=None,
        context=None,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = f"""
Perform reasoning and prepare actions with GIVEN TOOLS ONLY.
1. additional instruction: {instruction or "N/A"}. 
2. additional context: {context or "N/A"}.
"""
        if confidence_score:
            self.append_to_request("confidence_score")
