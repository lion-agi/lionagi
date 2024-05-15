from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate


class PlanTemplate(DirectiveTemplate):
    
    template_name: str = "plan_template"
    
    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )
    
    signature: str = "task -> plans"

    def __init__(
        self,
        *, 
        instruction=None,
        context=None, 
        confidence_score=False,
        reason=False,
        num_step=3,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = f"""
Generate a {num_step}_step plan based on the given context
1. additional instruction, {to_str(instruction or "N/A")}
2. additional context, {to_str(context or "N/A")}
"""
        if reason:
            self.append_to_request("reason")
            
        if confidence_score:
            self.append_to_request("confidence_score")
