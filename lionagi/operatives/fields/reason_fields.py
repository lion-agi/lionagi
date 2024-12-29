from lionagi.protocols.models.field_model import FieldModel
from lionagi.utils import to_num


def validate_confidence_score(cls, value) -> float:
    try:
        return to_num(
            value,
            upper_bound=1,
            lower_bound=0,
            num_type=float,
            precision=3,
        )
    except Exception:
        return -1


confidence_description = (
    "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating "
    "how well you've met user expectations. Use this guide:\n"
    "  • 1.0: Highly confident\n"
    "  • 0.8-1.0: Reasonably sure\n"
    "  • 0.5-0.8: Re-check or refine\n"
    "  • 0.0-0.5: Off track"
)

CONFIDENCE_SCORE_FIELD = FieldModel(
    name="confidence_score",
    annotation=float | None,
    default=None,
    title="Confidence Score",
    description=confidence_description,
    examples=[0.821, 0.257, 0.923, 0.439],
    validator=validate_confidence_score,
    validator_kwargs={"mode": "before"},
)
