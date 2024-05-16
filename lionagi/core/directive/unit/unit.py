from lionagi.libs.ln_func_call import rcall
from lionagi.core.generic.abc import Directive
from lionagi.core.validator.validator import Validator
from lionagi.core.generic import iModel
from .unit_mixin import DirectiveMixin
from ..util import retry_kwargs, _direct


class Unit(Directive, DirectiveMixin):
    """
    A class that represents a unit of action capable of performing various tasks
    such as chatting, acting, directing, selecting, and predicting. It leverages
    directives and mixins to perform these tasks asynchronously with retry logic.

    Attributes:
        branch (Branch): The branch of the session in which this unit operates.
        imodel (iModel): The model used for chat completion and other tasks.
        form_template (Template): The template used for forming instructions.
        validator (Validator): The validator used for validating responses.
        default_template (Template, optional): The default template for forms.
    """

    default_template = None

    def __init__(
        self, branch, imodel: iModel = None, template=None, rulebook=None
    ) -> None:
        """
        Initializes the Unit with the given branch, model, template, and rulebook.

        Args:
            branch (Branch): The branch of the session in which this unit operates.
            imodel (iModel, optional): The model used for chat completion and other tasks.
            template (Template, optional): The template used for forming instructions.
            rulebook (Rulebook, optional): The rulebook used for validating responses.
        """
        self.branch = branch
        if imodel and isinstance(imodel, iModel):
            branch.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = branch.imodel
        self.form_template = template or self.default_template
        self.validator = Validator(rulebook=rulebook) if rulebook else Validator()

    async def chat(self, *args, **kwargs):
        """
        Asynchronously performs a chat operation using the _chat method with retry logic.

        Args:
            *args: Positional arguments to pass to the _chat method.
            **kwargs: Keyword arguments to pass to the _chat method, including retry configurations.

        Returns:
            Any: The result of the chat operation.
        """
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(self._chat, *args, **kwargs)

    async def act(self, *args, **kwargs):
        """
        Asynchronously performs an act operation using the _act method with retry logic.

        Args:
            *args: Positional arguments to pass to the _act method.
            **kwargs: Keyword arguments to pass to the _act method, including retry configurations.

        Returns:
            Any: The result of the act operation.
        """
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(self._act, *args, **kwargs)

    async def direct(self, directive, *args, **kwargs):
        """
        Asynchronously performs a direct operation using the _direct method with retry logic.

        Args:
            directive (Any): The directive to execute.
            *args: Positional arguments to pass to the _direct method.
            **kwargs: Keyword arguments to pass to the _direct method, including retry configurations.

        Returns:
            Any: The result of the direct operation.
        """
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(_direct, directive, *args, **kwargs)

    async def select(self, *args, **kwargs):
        """
        Asynchronously performs a select operation using the _select method with retry logic.

        Args:
            *args: Positional arguments to pass to the _select method.
            **kwargs: Keyword arguments to pass to the _select method, including retry configurations.

        Returns:
            Any: The result of the select operation.
        """
        from .template.select import SelectTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", SelectTemplate)
        return await rcall(self._select, *args, **kwargs)

    async def predict(self, *args, **kwargs):
        """
        Asynchronously performs a predict operation using the _predict method with retry logic.

        Args:
            *args: Positional arguments to pass to the _predict method.
            **kwargs: Keyword arguments to pass to the _predict method, including retry configurations.

        Returns:
            Any: The result of the predict operation.
        """
        from .template.predict import PredictTemplate

        kwargs = {**retry_kwargs, **kwargs}
        kwargs["template"] = kwargs.get("template", PredictTemplate)
        return await rcall(self._predict, *args, **kwargs)
