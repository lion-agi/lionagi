from lionagi.libs import SysUtil
from abc import abstractmethod
from pandas import Series
from ..generic.abc import Condition, Actionable, Component


class Rule(Component, Condition, Actionable):
    """Combines a condition and an action that can be applied based on it."""

    apply_type: str = None
    fix: bool = False
    fields: list[str] = []
    validation_kwargs: dict = {}
    applied_log: list = []
    invoked_log: list = []
    _is_init: bool = False

    def add_log(self, field, form, apply=True, **kwargs):
        a = {
            "type": "rule",
            "class": self.class_name,
            "ln_id": self.ln_id,
            "timestamp": SysUtil.get_timestamp(sep=None)[:-6],
            "field": field,
            "form": form.ln_id,
            "config": kwargs,
        }
        if apply:
            self.applied_log.append(a)
        else:
            self.invoked_log.append(a)

    async def applies(
        self,
        field,
        value,
        form,
        *args,
        annotation: list[str] = None,
        use_annotation: bool = True,
        **kwargs,
    ):
        if self.fields:
            if field in self.fields:
                self.add_log(field, form, **kwargs)
                return True

        if use_annotation:
            annotation = annotation or form._get_field_annotation(field)
            annotation = [annotation] if isinstance(annotation, str) else annotation

            for i in annotation:
                if i in self.apply_type:
                    self.add_log(field, form, **kwargs)
                    return True
            return False

        a = await self.rule_condition(field, value, *args, **kwargs)

        if a:
            self.add_log(field, form, **kwargs)
            return True
        return False

    async def invoke(self, field, value, form):
        try:
            a = await self.validate(value, **self.validation_kwargs)
            self.add_log(field, form, apply=False, **self.validation_kwargs)
            return a

        except Exception as e1:
            if self.fix:
                try:
                    a = await self.perform_fix(value, **self.validation_kwargs)
                    self.add_log(field, form, apply=False, **self.validation_kwargs)
                    return a
                except Exception as e2:
                    raise ValueError(f"failed to fix field") from e2
            raise ValueError(f"failed to validate field") from e1

    async def rule_condition(self, *args, **kwargs) -> bool:
        """additional condition, if choose not to use annotation as qualifier"""
        return False

    async def perform_fix(self, value, *args, **kwargs):
        """return value or raise error"""
        return value

    @abstractmethod
    async def validate(self, value):
        """return value or raise error"""
        pass

    def _to_dict(self):
        return {
            "ln_id": self.ln_id[:8] + "...",
            "rule": self.__class__.__name__,
            "apply_type": self.apply_type,
            "fix": self.fix,
            "fields": self.fields,
            "validation_kwargs": self.validation_kwargs,
            "num_applied": len(self.applied_log),
            "num_invoked": len(self.invoked_log),
        }

    def __str__(self):
        series = Series(self._to_dict())
        return series.__str__()

    def __repr__(self):
        series = Series(self._to_dict())
        return series.__repr__()
