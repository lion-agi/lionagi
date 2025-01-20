# forms/flow.py

from pydantic import BaseModel, ConfigDict, Field


class FlowStep(BaseModel):
    """
    A minimal 'step' describing one transformation from some input fields to some output fields.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Identifier for the step.")
    inputs: list[str] = Field(
        ..., description="Which fields are needed for this step."
    )
    outputs: list[str] = Field(
        ..., description="Which fields are produced by this step."
    )
    description: str | None = None  # optional text doc


class FlowDefinition(BaseModel):
    """
    A minimal DSL-based multi-step flow, e.g. 'a,b->c; c->d' to yield two steps.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    steps: list[FlowStep] = Field(default_factory=list)

    def parse_flow_string(self, flow_str: str):
        """
        Parse a string like 'a,b->c; c->d' into multiple FlowSteps.
        We'll store them in self.steps in order.
        """
        if not flow_str:
            return
        segments = [seg.strip() for seg in flow_str.split(";") if seg.strip()]
        for i, seg in enumerate(segments):
            # seg might be like 'a,b->c' or 'a->b, c' etc
            if "->" not in seg:
                raise ValueError(f"Invalid DSL segment (no '->'): '{seg}'")
            ins_str, outs_str = seg.split("->", 1)
            inputs = [x.strip() for x in ins_str.split(",") if x.strip()]
            outputs = [y.strip() for y in outs_str.split(",") if y.strip()]
            step = FlowStep(name=f"step_{i+1}", inputs=inputs, outputs=outputs)
            self.steps.append(step)

    def get_required_fields(self) -> set[str]:
        """
        Return all fields that are used as inputs in the earliest steps but not produced by prior steps.
        This is a minimal approach; or we can do more advanced logic if needed.
        """
        produced = set()
        required = set()
        for step in self.steps:
            # anything not yet produced is needed
            for i in step.inputs:
                if i not in produced:
                    required.add(i)
            for o in step.outputs:
                produced.add(o)
        return required

    def get_produced_fields(self) -> set[str]:
        """
        Return all fields that eventually get produced by any step.
        """
        result = set()
        for st in self.steps:
            result.update(st.outputs)
        return result
