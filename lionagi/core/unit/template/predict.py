from .base import BaseUnitForm, Field


class PredictTemplate(BaseUnitForm):
    """
    A template for predicting the next sentence(s) based on given instructions and context.

    Inherits from `BaseUnitForm` and adds fields and methods specific to prediction tasks.

    Attributes:
        confidence_score (float | None): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the prediction.
        reason (str | None): A brief reason for the given output.
        template_name (str): The name of the template.
        num_sentences (int): The number of sentences to predict.
        prediction (None | str | list): The predicted sentence(s) or desired output.
        assignment (str): A string representing the task assignment for the prediction.
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
        None,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "predict_template"

    num_sentences: int = Field(
        2, description="the number of sentences to predict"
    )

    prediction: None | str | list = Field(
        None,
        description="the predicted sentence(s) or desired output",
    )

    assignment: str = "task -> prediction"

    @property
    def answer(self):
        """
        Gets the prediction attribute.

        Returns:
            None | str | list: The predicted sentence(s) or desired output.
        """
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
        """
        Initializes a new instance of the PredictTemplate class.

        Args:
            instruction (str, optional): Additional instructions for the prediction.
            context (str, optional): Additional context for the prediction.
            num_sentences (int, optional): The number of sentences to predict. Defaults to 2.
            confidence_score (bool, optional): Whether to include a confidence score. Defaults to False.
            reason (bool, optional): Whether to include a reasoning field. Defaults to False.
            **kwargs: Additional keyword arguments.
        """

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
