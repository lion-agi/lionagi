from enum import Enum
from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate


class SelectTemplate(DirectiveTemplate):

    template_name: str = "default_select"

    selection: Enum | str | list = Field(
        default_factory=str, description="selection from given choices"
    )
    choices: list = Field(default_factory=list, description="the given choices")

    signature: str = "task -> selection"

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
