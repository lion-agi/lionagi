from lionagi.libs.ln_func_call import rcall
from lionagi.core.generic.abc import Directive
from lionagi.core.validator.validator import Validator
from lionagi.core.generic import iModel

from .unit_mixin import DirectiveMixin
from ..util import retry_kwargs, _direct


class Unit(Directive, DirectiveMixin):

    default_template = None

    def __init__(
        self, branch, imodel: iModel = None, template=None, rulebook=None
    ) -> None:
        self.branch = branch
        if imodel and isinstance(imodel, iModel):
            branch.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = branch.imodel
        self.form_template = template or self.default_template
        self.validator = Validator(rulebook=rulebook) if rulebook else Validator()

    async def chat(self, *args, **kwargs):
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(self._chat, *args, **kwargs)

    async def act(self, *args, **kwargs):
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(self._act, *args, **kwargs)

    async def direct(self, directive, *args, **kwargs):
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(_direct, directive, *args, **kwargs)

    async def select(self, *args, **kwargs):
        from .template.select import SelectTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", SelectTemplate)
        return await rcall(self._select, *args, **kwargs)

    async def predict(self, *args, **kwargs):
        from .template.predict import PredictTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", PredictTemplate)
        return await rcall(self._predict, *args, **kwargs)
