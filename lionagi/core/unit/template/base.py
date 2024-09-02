from lionagi.core.collections.abc import Field
from lionagi.core.report.form import Form

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class BaseUnitForm(Form):
    """
    A base form class for units that includes fields for confidence scoring and reasoning.

    Attributes:
        template_name (str): The name of the template.
        confidence_score (float): A numeric confidence score between 0 and 1 with precision to 2 decimal places.
        reason (str | None): A field for providing concise reasoning for the process.
    """

    template_name: str = "UnitDirective"

    confidence_score: float = Field(
        None,
        description=(
            "Provide a numeric confidence score on how likely you successfully achieved the task  between 0 and 1, with precision in 2 decimal places. 1 being very confident in a good job, 0 is not confident at all."
        ),
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        None,
        description=(
            "Explain yourself, provide concise reasoning for the process. Must start with: Let's think step by step, "
        ),
    )
