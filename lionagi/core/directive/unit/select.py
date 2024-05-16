from enum import Enum
from lionagi.core.generic.abc import Field
from .base import UnitDirective, Chat
from lionagi.core.session.branch import Branch

from lionagi.core.report.form import Form


class SelectTemplate(Form):

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
    choices: list = Field(default_factory=list, description="the given choices")

    assignment: str = "task -> selection"

    @property
    def answer(self):
        return self.selection

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


class Select(UnitDirective):

    async def _select(
        self,
        form=None,
        choices=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        context=None,
        branch=None,
        system=None,
        **kwargs,
    ):

        branch = branch or Branch(system=system)

        if not form:
            form = SelectTemplate(
                choices=choices,
                reason=reason,
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
            )

        directive = Chat(branch)
        return await directive.chat(form=form, return_form=True, **kwargs)

    async def select(self, *args, **kwargs):
        return await self._select(*args, **kwargs)

    async def direct(self, *args, **kwargs):
        return await self._select(*args, **kwargs)
