from pydantic import Field
from lionagi.libs import func_call
from ..prompt.prompt_template import ScoredTemplate
from ..branch import Branch


class PredictTemplate(ScoredTemplate):
    template_name: str = "default_predict_template"
    sentence: str | list | dict = Field(
        default_factory=str, description="the given sentence(s) to predict"
    )
    num_sentences: int = Field(
        default_factory=int, description="the number of sentences to predict"
    )
    answer: str | list = Field(
        default_factory=str, description="the predicted sentence(s)"
    )
    signature: str = "sentence -> answer"

    def __init__(
        self,
        sentence=None,
        num_sentences=None,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.num_sentences = num_sentences
        self.task = f"predict the next {self.num_sentences} sentence(s)"

        if reason:
            self.output_fields.append("reason")

        if confidence_score:
            self.output_fields.append("confidence_score")


async def predict(
    sentence,
    num_sentences=1,
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

    predict_template = PredictTemplate(
        sentence=sentence,
        num_sentences=num_sentences,
        confidence_score=confidence_score,
        reason=reason,
    )

    await func_call.rcall(
        branch.chat,
        prompt_template=predict_template,
        retries=retries,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default_value,
        timeout=timeout,
        **kwargs,
    )

    return predict_template
