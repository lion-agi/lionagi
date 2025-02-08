# forms/flow.py

from typing import Any, Callable, List, Optional

from pydantic import BaseModel, Field

from lionagi.operatives.forms.form import Form
from lionagi.protocols.generic.event import Event, EventStatus


class FlowStep(BaseModel):
    """
    A single step in a multi-step flow:
      - name: identifier
      - inputs: which form fields we read
      - outputs: which form fields we write
      - transform_function: optional callable that transforms input field values
         into output field values. If None, do a pass-through mapping.

    Example: If transform_function is greet(name), then inputs=["name"], outputs=["greeting"].
    """

    name: str = Field(..., description="Identifier for the step.")
    inputs: List[str] = Field(
        default_factory=list, description="Fields read from the Form"
    )
    outputs: List[str] = Field(
        default_factory=list, description="Fields written into the Form"
    )
    description: Optional[str] = None

    # The user can provide a function that processes the input values
    transform_function: Optional[Callable[..., Any]] = Field(
        default=None,
        description="If set, transform_function(*input_values) => output_value(s).",
    )

    def run(self, form: Form) -> None:
        """
        Execute this step on the given form:
          1) Gather input values from the Form
          2) If transform_function is provided, call it
             else do a pass-through
          3) Assign results to output fields in the form
        """
        # Gather inputs
        input_values = [getattr(form, f, None) for f in self.inputs]

        # If there's a transform function, call it
        if self.transform_function:
            result = self.transform_function(*input_values)
        else:
            # trivial pass-through: check #inputs == #outputs
            if len(self.inputs) != len(self.outputs):
                raise ValueError(
                    f"Step {self.name}: no transform_function + mismatch. "
                    f"{len(self.inputs)} inputs vs. {len(self.outputs)} outputs"
                )
            result = input_values

        # Write to output fields
        if isinstance(result, dict):
            # dictionary keys => attempt matching them to output fields
            for k, v in result.items():
                if k in self.outputs:
                    setattr(form, k, v)

        elif isinstance(result, (list, tuple)):
            # must match the # of outputs
            if len(result) != len(self.outputs):
                raise ValueError(
                    f"Step {self.name}: transform_function returned {len(result)} items, but "
                    f"there are {len(self.outputs)} output fields."
                )
            for out_f, val in zip(self.outputs, result):
                setattr(form, out_f, val)
        else:
            # single scalar => must be exactly one output
            if len(self.outputs) != 1:
                raise ValueError(
                    f"Step {self.name}: transform_function returned a single value, but "
                    f"there are {len(self.outputs)} output fields."
                )
            setattr(form, self.outputs[0], result)


class FlowDefinition(BaseModel):
    """
    A pipeline of FlowSteps. Optionally parse a DSL, e.g. "a,b->c; c->d"
    which creates multiple steps with pass-through transform.
    """

    name: str = Field(..., description="Name for the entire flow definition.")
    steps: List[FlowStep] = Field(
        default_factory=list, description="Ordered steps in the pipeline"
    )

    def parse_flow_string(self, flow_str: str):
        """
        Parse a DSL like "a,b->c; c->d" => step_1(inputs=[a,b], outputs=[c]),
                                           step_2(inputs=[c],   outputs=[d])
        transform_function is None => pass-through
        """
        if not flow_str:
            return
        segments = [seg.strip() for seg in flow_str.split(";") if seg.strip()]
        for i, seg in enumerate(segments):
            if "->" not in seg:
                raise ValueError(f"Invalid DSL segment (no '->'): '{seg}'")
            left, right = seg.split("->", 1)
            ins = [x.strip() for x in left.split(",") if x.strip()]
            outs = [y.strip() for y in right.split(",") if y.strip()]

            step = FlowStep(
                name=f"step_{i+1}",
                inputs=ins,
                outputs=outs,
                transform_function=None,  # pass-through
            )
            self.steps.append(step)

    def run_all(self, form: Form) -> None:
        """Run each step in order, modifies the Form in-place."""
        for step in self.steps:
            step.run(form)

    def get_required_fields(self) -> set[str]:
        """
        Basic check: fields that appear as step inputs but were never
        produced by a prior step's outputs.
        """
        produced = set()
        required = set()
        for st in self.steps:
            for i in st.inputs:
                if i not in produced:
                    required.add(i)
            for o in st.outputs:
                produced.add(o)
        return required

    def get_produced_fields(self) -> set[str]:
        """
        All fields that eventually appear as outputs in any step.
        """
        result = set()
        for st in self.steps:
            result.update(st.outputs)
        return result


class FlowTask(Event):
    """
    An Event that references a FlowDefinition and a Form.
    You can run all steps or pick up from current_step if partial runs are needed.

    On invoke(), it attempts to run from current_step through the end.
    """

    definition: FlowDefinition = Field(
        ..., description="The pipeline of steps to apply"
    )
    form: Form = Field(
        ..., description="The form that holds the input/output fields"
    )
    current_step: int = Field(
        0, description="Index of next step to run within definition"
    )

    async def invoke(self) -> None:
        self.status = EventStatus.PROCESSING
        try:
            while self.current_step < len(self.definition.steps):
                step = self.definition.steps[self.current_step]
                step.run(self.form)
                self.current_step += 1

            self.status = EventStatus.COMPLETED
            self.execution.response = {
                "completed_steps": self.current_step,
                "final_form_outputs": self.form.get_results(valid_only=False),
            }
        except Exception as e:
            self.status = EventStatus.FAILED
            self.execution.error = str(e)

    async def stream(self) -> None:
        """
        If partial or streaming logic is needed, you can break out each step.
        For now, just do the same as invoke().
        """
        await self.invoke()
