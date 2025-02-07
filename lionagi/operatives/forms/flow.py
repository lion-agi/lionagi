"""
A refactored Flow system that:
 - Keeps the existing FlowDefinition & FlowStep with DSL parsing
 - Adds a 'transform_function' to each FlowStep for advanced logic
 - Provides a FlowTask (Event) that runs all steps in sequence on a Form.
"""

from typing import List, Callable, Any, Optional
from pydantic import BaseModel, Field

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.operatives.forms.form import Form


class FlowStep(BaseModel):
    """
    A single step in a multi-step flow:
      - name: identifier
      - inputs: which form fields we read
      - outputs: which form fields we write
      - description: optional text
      - transform_function: optional callable that transforms input field values
         into output field values.

    If no transform_function is provided, we do a trivial pass-through
    (the first input is copied to the first output, second input to second output, etc.).
    """

    name: str = Field(..., description="Identifier for the step.")
    inputs: List[str] = Field(
        default_factory=list, description="Fields read from the Form"
    )
    outputs: List[str] = Field(
        default_factory=list, description="Fields written into the Form"
    )
    description: Optional[str] = None

    # Optional transform function. If None, we do pass-through.
    transform_function: Optional[Callable[..., Any]] = Field(
        default=None,
        description="If set, this is called as transform_function(*input_values) -> output_value(s).",
    )

    def run(self, form: Form) -> None:
        """
        Execute this step on the given form:
          1. Gather input values from the Form
          2. If transform_function is present, call it
             else do pass-through
          3. Store results in the output fields
        """
        # 1) Gather input values from the form
        input_values = [getattr(form, f, None) for f in self.inputs]

        # 2) Execute transform or pass-through
        if self.transform_function:
            result = self.transform_function(*input_values)
        else:
            # trivial pass-through logic
            # if #inputs == #outputs, pair them up
            if len(self.inputs) != len(self.outputs):
                raise ValueError(
                    f"Step {self.name}: no transform_function and inputs/outputs mismatch: "
                    f"{len(self.inputs)} inputs vs. {len(self.outputs)} outputs"
                )
            # We'll just return a list of the same input_values
            # so that input[i] is assigned to output[i].
            result = input_values

        # 3) Write results to output fields
        if isinstance(result, dict):
            # dictionary keys should match output field names if you want them stored
            for k, v in result.items():
                if k in self.outputs:
                    setattr(form, k, v)
        elif isinstance(result, (list, tuple)):
            # if there's exactly one output but the function returned multiple,
            # that is an error. Or if there's multiple outputs and lengths mismatch, error.
            if len(self.outputs) == 1 and len(result) != 1:
                raise ValueError(
                    f"Step {self.name}: transform_function returned multiple values but there's only 1 output field."
                )
            if len(result) != len(self.outputs):
                raise ValueError(
                    f"Step {self.name}: mismatch in # of returned items {len(result)} vs # of outputs {len(self.outputs)}"
                )
            for out_field, val in zip(self.outputs, result):
                setattr(form, out_field, val)
        else:
            # single value to store if we have exactly 1 output
            if len(self.outputs) != 1:
                raise ValueError(
                    f"Step {self.name}: transform_function returned a single value, "
                    f"but there are {len(self.outputs)} output fields."
                )
            setattr(form, self.outputs[0], result)


class FlowDefinition(BaseModel):
    """
    Defines a multi-step transformation pipeline with a list of FlowSteps.

    Also includes optional DSL parsing e.g. "a,b->c; c->d" to create multiple steps:
      step_1: inputs=[a,b], outputs=[c]
      step_2: inputs=[c],   outputs=[d]

    If transform_function is not set in a step, do a trivial pass-through
    from step inputs to step outputs.
    """

    name: str = Field(..., description="Name for the entire flow definition.")
    steps: List[FlowStep] = Field(
        default_factory=list, description="Ordered sequence of steps"
    )

    def parse_flow_string(self, flow_str: str):
        """
        Parse a DSL like "a,b->c; c->d" into multiple steps, appended to self.steps.
        Each step is named step_{i+1}.
        No transform_function is assigned by default; they'd do pass-through logic
        or you can set transform_function manually afterward.
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
                transform_function=None,  # pass-through by default
            )
            self.steps.append(step)

    def run_all(self, form: Form) -> None:
        """
        Run all steps in sequence, modifying the form in-place.
        """
        for step in self.steps:
            step.run(form)

    def run_step(self, index: int, form: Form) -> None:
        """
        Run only the step at position index. (0-based)
        """
        if index < 0 or index >= len(self.steps):
            raise IndexError(f"Step index {index} is out of range.")
        self.steps[index].run(form)

    def get_required_fields(self) -> set[str]:
        """
        Return fields needed as inputs in the earliest step(s) 
        but not produced by earlier steps. (Basic logic.)
        """
        produced = set()
        required = set()
        for step in self.steps:
            # any input not in produced is needed externally
            for i_ in step.inputs:
                if i_ not in produced:
                    required.add(i_)
            for o_ in step.outputs:
                produced.add(o_)
        return required

    def get_produced_fields(self) -> set[str]:
        """
        Return all fields eventually produced by any step in the flow.
        """
        result = set()
        for st in self.steps:
            result.update(st.outputs)
        return result


class FlowTask(Event):
    """
    An Event that references:
     - A FlowDefinition (the pipeline)
     - A Form (the data object that has the needed fields)
     - current_step: which step index to run next

    On invoke(), it runs from current_step to the end, 
    marking status COMPLETED or FAILED accordingly.
    """

    definition: FlowDefinition = Field(
        ..., description="The pipeline of steps to apply"
    )
    form: Form = Field(
        ..., description="The form that holds input+output fields."
    )
    current_step: int = Field(
        0, description="Index of next step to run within definition."
    )

    async def invoke(self) -> None:
        """
        Run from current_step onward. If we succeed in all steps, mark COMPLETED.
        If any step fails, we mark FAILED and store the error.
        """
        self.status = EventStatus.PROCESSING
        try:
            while self.current_step < len(self.definition.steps):
                self.definition.run_step(self.current_step, self.form)
                self.current_step += 1

            # Done, mark COMPLETED
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
        If partial or streaming is needed, you can implement chunked logic. 
        For now, just the same as invoke().
        """
        await self.invoke()
        
        
# import asyncio
# from lionagi.operatives.forms.form import Form
# from forms.flow import FlowStep, FlowDefinition, FlowTask


# # 1) Suppose we define a transform function
# def greet(name: str) -> str:
#     return f"Hello, {name}!"

# # 2) Create a FlowDefinition (manually or via parse_flow_string)
# definition = FlowDefinition(name="GreetingFlow")
# step1 = FlowStep(
#     name="GreetingStep",
#     inputs=["user_name"],
#     outputs=["greeting"],
#     transform_function=greet,
# )
# definition.steps.append(step1)

# # 3) Or you can parse DSL for some steps with pass-through, etc.
# # definition.parse_flow_string("user_name -> greeting")  # pass-through version
# # Then assign a transform_function if needed.

# # 4) Our form
# class GreetForm(Form):
#     user_name: str | None = None
#     greeting: str | None = None

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.output_fields = ["greeting"]  # we want 'greeting' as final output

# my_form = GreetForm(user_name="Alice")

# # 5) Create a FlowTask referencing the definition and form
# task = FlowTask(definition=definition, form=my_form)

# # 6) Run it
# async def run_it():
#     await task.invoke()
#     print(task.status)  # Should be COMPLETED
#     print("Final form outputs:", task.execution.response)

# asyncio.run(run_it())
# # Expected: 
# # EventStatus.COMPLETED
# # Final form outputs: { "completed_steps":1, "final_form_outputs":{"user_name":"Alice","greeting":"Hello, Alice!"} }