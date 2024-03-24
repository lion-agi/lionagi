from enum import Enum
from pydantic import Field

from lionagi.libs import func_call, StringMatch
from ..prompt.prompt_template import ScoredTemplate
from ..branch import Branch


class SelectTemplate(ScoredTemplate):
    template_name: str = "default_select"
    sentence: str | list | dict = Field(default_factory=str, description="the given context")
    answer: Enum | str = Field(default_factory=str, description="selection from given choices")
    
    signature: str = "sentence -> answer"

    def __init__(
        self,
        sentence=None,
        choices=None,
        num_choices=1,
        instruction=None,
        reason=False, 
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.choices = choices
        self.task = f"select {num_choices} item(s), from provided choices {choices}."
        if instruction:
            self.task += f"objetive {instruction}."
        
        if reason:
            self.output_fields.append("reason")

        if confidence_score:
            self.output_fields.append("confidence_score")


async def select(
    sentence,
    choices=None,
    num_choices=1,
    instruction=None,
    confidence_score=False,
    reason=False,
    retries=2,
    delay=0.5,
    backoff_factor=2,
    default_value=None,
    timeout=None,
    branch_name=None,
    system=None,
    messages=None,
    service=None,
    sender=None,
    llmconfig=None,
    tools=None,
    datalogger=None,
    persist_path=None,
    tool_manager=None,
    **kwargs,
):

    branch = Branch(
        name=branch_name,
        system=system,
        messages=messages,
        service=service,
        sender=sender,
        llmconfig=llmconfig,
        tools=tools,
        datalogger=datalogger,
        persist_path=persist_path,
        tool_manager=tool_manager,
    )

    _template = SelectTemplate(
        sentence=sentence,
        choices=choices,
        num_choices=num_choices,
        instruction=instruction,
        confidence_score=confidence_score,
        reason=reason,
    )

    await func_call.rcall(
        branch.chat,
        prompt_template=_template,
        retries=retries,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default_value,
        timeout=timeout,
        **kwargs,
    )

    ans = _template.answer
    if ans not in _template.choices:
        _template.answer = StringMatch.choose_most_similar(ans, _template.choices)

    return _template
