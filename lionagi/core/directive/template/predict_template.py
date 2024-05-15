from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate


class PredictTemplate(DirectiveTemplate):

    template_name: str = "predict_template"

    num_sentences: int = Field(
        1, 
        description="the number of sentences to predict"
    )
    
    prediction: str | list = Field(
        default_factory=str, 
        description="the predicted sentence(s) or desired output"
    )
    
    signature: str = "task -> prediction"

    def __init__(
        self,
        *, 
        instruction=None, 
        context=None,
        num_sentences=1,
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
