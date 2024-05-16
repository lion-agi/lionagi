from .base import UnitForm, Field


class ActionTemplate(UnitForm):

    action_required: bool | None = Field(
        None, description="True if actions are needed else False"
    )

    actions: list[dict] | None = Field(
        None,
        description="""
provide The list of action(s) to take, [{"function": func, "arguments": {"param1":..., "param2":..., ...}}, ...] Leave blank if no further actions are needed, you must use provided parameters for each action, DO NOT MAKE UP NAME!!!
""",
    )

    answer: str | None = Field(
        None,
        description="output answer to the questions asked if further actions are not needed, leave blank if an accurate answer cannot be provided from context during this step",
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
3. Absolutely DO NOT MAKE UP FUNCTIONS !!!
"""
        if confidence_score:
            self.append_to_request("confidence_score")
