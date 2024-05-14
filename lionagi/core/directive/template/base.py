from typing import Any
from lionagi.core.report.form import Form
from lionagi.core.generic.abc import Field

class DirectiveTemplate(Form):
    
    confidence_score: float = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        
        validation_kwargs={
            "upper_bound": 1, 
            "lower_bound": 0, 
            "num_type": float, 
            "precision": 2
        }
    )

    reason: str = Field(
        default_factory=str,
        description="brief reason for the given output, format: This is my best response because ...",
    )