from .base import UnitForm, Field


class PredictTemplate(UnitForm):

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
        None,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "predict_template"

    num_sentences: int = Field(2, description="the number of sentences to predict")

    prediction: None | str | list = Field(
        None,
        description="the predicted sentence(s) or desired output",
    )

    assignment: str = "task -> prediction"

    @property
    def answer(self):
        return getattr(self, "prediction", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        num_sentences=2,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.num_sentences = num_sentences

        self.task = f"""
predict the next sentence(s) according to the following constraints
1. number of sentences: {self.num_sentences}
2. additional objective , {instruction or "N/A"}
3. additional information, {context or "N/A"}
"""

        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")
