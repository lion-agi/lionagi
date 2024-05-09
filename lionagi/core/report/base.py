from abc import ABC, abstractmethod
from typing import Any
import contextlib
from ..generic.abc import Component, Field
from ..generic.util import to_list_type


class BaseForm(ABC, Component):
    assignment: str = Field(..., examples=["input1, input2 -> output"])
    input_fields: list[str] = Field(default_factory=list)
    requested_fields: list[str] = Field(default_factory=list)

    @abstractmethod
    @property
    def work_fields(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def fill(self, /, *args, **kwargs):
        pass

    @abstractmethod
    def is_workable(self) -> bool:
        pass

    @property
    def filled(self) -> bool:
        with contextlib.suppress(ValueError):
            return self._is_filled()
        return False

    @property
    def workable(self) -> bool:
        with contextlib.suppress(ValueError):
            return self.is_workable()
        return False

    def _is_filled(self):
        for k, value in self.work_fields.items():
            if value is None:
                raise ValueError(f"Field {k} is not filled")
        return True

    def _get_all_fields(self, form=None, **kwargs):
        """
        given a form, or collections of a form, and additional fields,
        gather all fields together including self fields with valid value
        """
        form: list["BaseForm"] = to_list_type(form) if form else []
        all_fields = self.work_fields.copy()
        all_form_fields = (
            {}
            if not form
            else {k: v for i in form for k, v in i.work_fields.items() if v is not None}
        )
        all_fields.update({**all_form_fields, **kwargs})
        return all_fields
