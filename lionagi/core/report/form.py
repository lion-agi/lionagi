from ..generic.abc.util import SYSTEM_FIELDS
from .util import get_input_output_fields
from .base import BaseForm
from ..validator.validator import Validator


class Form(BaseForm):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )
        for i in self.input_fields + self.requested_fields:
            if i not in self._all_fields:
                self._add_field(i, value=None)

    @property
    def work_fields(self):
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in SYSTEM_FIELDS and k in self.input_fields + self.requested_fields
        }

    def fill(self, form: "Form" = None, **kwargs):
        if self.filled:
            raise ValueError("Form is already filled")

        all_fields = self._get_all_fields(form, **kwargs)

        for k, v in all_fields.items():
            if (
                k in self.work_fields
                and v is not None
                and getattr(self, k, None) is None
            ):
                setattr(self, k, v)

    def is_workable(self):
        if self.filled:
            raise ValueError("Form is already filled, cannot be worked on again")

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        return True

    async def _process_response(self, response, strict=False, validator=Validator()):
        if isinstance(response, str):
            if len(self.requested_fields) == 1:
                self.fill(**{self.requested_fields[0]: response})
                return
        else:
            dict_ = {}
            for k, v in response.items():

                if k in self.requested_fields:
                    _annotation = self._field_annotations[k]

                    if (
                        _choices := self._get_field_attr(k, "choices", None)
                    ) is not None:
                        await validator.validate(
                            v, _annotation, strict=strict, choices=_choices
                        )

                    elif (_keys := self._get_field_attr(k, "keys", None)) is not None:
                        if not "dict" in str(_annotation):
                            raise ValueError(
                                f"keys attribute is only applicable to dict fields"
                            )
                        await validator.validate(
                            v, _annotation, strict=strict, keys=_keys
                        )

                    else:
                        await validator.validate(v, _annotation, strict=strict)

                    dict_[k] = v

            self.fill(**dict_)
