from lionagi.core.collections.abc import Field
from lionagi.core.report.form import Form


class BaseUnitForm(Form):
    template_name: str = "UnitDirective"

    confidence_score: float = Field(
        None,
        description=(
            "Provide a numeric confidence score between 0 and 1. Format: num:0.2f. 1 "
            "is very confident, 0 is not confident at all."
        ),
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        }
    )

    reason: str | None = Field(
        None,
        description=(
            "Provide a brief reason for the output. Must start with: Let's think step by step, "
            "because ..."
        )
    )

