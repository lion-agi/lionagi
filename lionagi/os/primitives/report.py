# from typing import Type
# from pydantic import Field

# from lion_core.form.report import Report as CoreReport
# from lionagi.os.primitives.pile import Pile
# from lionagi.os.primitives.form import Form


# class Report(CoreReport):

#     default_form_template: Type[Form] = Form
#     strict_form: bool = Field(
#         default=False,
#         description="Indicate whether the form is strict. "
#         "If True, the form cannot be modified after init.",
#     )

#     completed_tasks: Pile[Form] = Field(
#         default_factory=lambda: Pile(item_type={Form}),
#         description="A pile of tasks completed",
#     )


# __all__ = ["Report"]
