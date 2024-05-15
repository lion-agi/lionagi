from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate

class ScoreTemplate(DirectiveTemplate):
    
    template_name: str = "score_template"
    
    score: float = Field(
        None,
        description="a score for the given context and task, numeric",
    )
    
    signature: str = "task -> score"

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        score_range=(1, 10),
        inclusive=True,
        num_digit=0,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
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
3. include_endpoints: {"yes" if inclusive else "no"}.
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
