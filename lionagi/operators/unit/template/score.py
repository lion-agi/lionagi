from lionagi.core.collections.abc import Field
from lionagi.core.unit import UnitForm
from lionagi.libs.ln_convert import to_str


class ScoreTemplate(UnitForm):
    """
    A template for performing a scoring task based on given instructions and context.

    Inherits from `UnitForm` and adds fields and methods specific to scoring tasks.

    Attributes:
        confidence_score (float | None): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the score.
        reason (str | None): A brief reason for the given output.
        template_name (str): The name of the template.
        score (float | None): A score for the given context and task.
        assignment (str): A string representing the task assignment for the score.
    """

    confidence_score: float | None = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all",
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

    template_name: str = "score_template"

    score: float | None = Field(
        None,
        description="a score for the given context and task, numeric",
    )

    assignment: str = "task -> score"

    @property
    def answer(self):
        """
        Gets the score attribute.

        Returns:
            float | None: The score for the given context and task.
        """
        return getattr(self, "score", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        score_range=(0, 10),
        include_endpoints=True,
        num_digit=0,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
        """
        Initializes a new instance of the ScoreTemplate class.

        Args:
            instruction (str, optional): Additional instructions for the scoring task.
            context (str, optional): Additional context for the scoring task.
            score_range (tuple, optional): The range of the score. Defaults to (0, 10).
            include_endpoints (bool, optional): Whether to include the endpoints in the score range. Defaults to True.
            num_digit (int, optional): The number of digits allowed after the decimal point. Defaults to 0.
            confidence_score (bool, optional): Whether to include a confidence score. Defaults to False.
            reason (bool, optional): Whether to include a reasoning field. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        return_precision = ""

        if num_digit == 0:
            return_precision = "integer"
        else:
            return_precision = f"num:{to_str(num_digit)}f"

        self.task = f"""
perform scoring task according to the following constraints:
1. additional objective: {to_str(instruction or "N/A")}.
2. score range: {to_str(score_range)}.
3. include_endpoints: {"yes" if include_endpoints else "no"}.
4. precision, (max number of digits allowed after "."): {return_precision}.
5. additional information: {to_str(context or "N/A")}.
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")

        self.validation_kwargs["score"] = {
            "upper_bound": score_range[1],
            "lower_bound": score_range[0],
            "num_type": int if num_digit == 0 else float,
            "precision": num_digit if num_digit != 0 else None,
        }
