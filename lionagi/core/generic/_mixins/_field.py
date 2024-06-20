from functools import singledispatchmethod
from typing import Any
from pydantic import Field
from lionagi.os.lib import strip_lower
from ...generic.exceptions import FieldError, LionTypeError


class ComponentFieldMixin:
    
    def _add_field(
        self,
        field: str,
        annotation: Any = None,
        default: Any = None,
        value: Any = None,
        field_obj: Any = None,
        **kwargs,
    ) -> None:
        """Add a field to the model after initialization."""
        self.extra_fields[field] = field_obj or Field(default=default, **kwargs)
        if annotation:
            self.extra_fields[field].annotation = annotation

        if not value and (a := self._get_field_attr(field, "default", None)):
            value = a

        self.__setattr__(field, value)

    def add_field(self, field, value, annotation=None, **kwargs):
        self._add_field(field, annotation, value=value, **kwargs)

    @property
    def all_fields(self):
        return {**self.model_fields, **self.extra_fields}

    @property
    def field_annotations(self) -> dict:
        """Return the annotations for each field in the model."""
        return self._get_field_annotation(list(self.all_fields.keys()))

    def _get_field_attr(self, k: str, attr: str, default: Any = False) -> Any:
        """Get the value of a field attribute."""
        try:
            if not self._field_has_attr(k, attr):
                raise FieldError(f"field {k} has no attribute {attr}")

            field = self.all_fields[k]
            if not (a := getattr(field, attr, None)):
                try:
                    return field.json_schema_extra[attr]
                except Exception:
                    return None
            return a
        except Exception as e:
            if default is not False:
                return default
            raise e

    @singledispatchmethod
    def _get_field_annotation(self, field_name: Any) -> Any:
        raise LionTypeError

    @_get_field_annotation.register(str)
    def _(self, field_name: str) -> dict[str, Any]:
        dict_ = {field_name: self.all_fields[field_name].annotation}
        for k, v in dict_.items():
            if "|" in str(v):
                v = str(v)
                v = v.split("|")
                dict_[k] = [strip_lower(i) for i in v]
            else:
                dict_[k] = [v.__name__] if v else None
        return dict_

    @_get_field_annotation.register(list)
    @_get_field_annotation.register(tuple)
    def _(self, field_names: list | tuple) -> dict[str, Any]:
        dict_ = {}
        for field_name in field_names:
            dict_.update(self._get_field_annotation(field_name))
        return dict_

    def _field_has_attr(self, k: str, attr: str) -> bool:
        """Check if a field has a specific attribute."""
        if not (field := self.all_fields.get(k, None)):
            raise KeyError(f"Field {k} not found in model fields.")

        if attr not in str(field):
            try:
                a = (
                    attr in self.all_fields[k].json_schema_extra
                    and self.all_fields[k].json_schema_extra[attr] is not None
                )
                return a if isinstance(a, bool) else False
            except Exception:
                return False
        return True
