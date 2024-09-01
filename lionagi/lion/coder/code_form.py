from typing import Any
from pydantic import Field
from lionagi.libs import ParseUtil, SysUtil
from lionagi.core import Session
from lionagi.core.form.action_form import ActionForm


class CodeForm(ActionForm):
    template_name: str = "code_form"
    language: str = Field(
        default="python",
        description="The programming language of the code to be executed.",
    )
