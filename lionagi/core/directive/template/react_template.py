from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate


class ReactTemplate(DirectiveTemplate):
    template_name: str = "react_template"
    
    action_required: bool = Field(
        False, description="true if actions are needed else false"
    )
    
    actions: list[dict] = Field(
        None, 
        description="""
provide The list of action(s) to take, each action in format of 
{"function": function_name, "arguments": {param1:..., param2:..., ...}}. 
Leave blank if no further actions are needed, 
you must use provided parameters for each action, DO NOT MAKE UP NAME!!!
"""
    )

    answer: str | dict | None = Field(
        default_factory=str,
        description="output answer to the questions asked if further actions are not needed, leave blank if an accurate answer cannot be provided from context during this step",
    )

    signature: str = "task -> reason, action_needed, actions, answer"
    

    def __init__(
        self,
        *, 
        instruction=None,
        context=None,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = f"""
Perform reasoning and prepare actions with GIVEN TOOLS ONLY.
1. additional objective: {instruction or "N/A"}. 
2. additional information: {context or "N/A"}.
3. Absolutely DO NOT MAKE UP FUNCTIONS !!!
"""
        if confidence_score:
            self.append_to_request("confidence_score")
            