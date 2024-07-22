from lion_core.abc import BaseProcessor
from lion_core.libs import rcall
from lion_core.imodel.imodel import iModel
from lion_core.validator.validator import Validator
from .chat_mixin import UnitChatMixin
from .act_mixin import UnitActMixin
from .direct_mixin import UnitDirectMixin
from .unit_form import UnitForm
from .utils import retry_kwargs


class UnitProcessor(BaseProcessor, UnitChatMixin, UnitActMixin, UnitDirectMixin):
    """
    Unit is a class that extends Directive and DirectiveMixin to provide
    advanced operations like chat, direct actions, and predictions using a
    specific branch and model.

    Attributes:
        branch (Branch): The branch instance associated with the Unit.
        imodel (iModel): The model instance used for the Unit.
        form_template (Type[Form]): The form template to use for operations.
        validator (Validator): The validator instance for response validation.
    """

    default_template = UnitForm

    def __init__(
        self, branch, imodel: iModel = None, template=None, rulebook=None, verbose=False
    ) -> None:
        self.branch = branch
        if imodel and isinstance(imodel, iModel):
            branch.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = branch.imodel
        self.form_template = template or self.default_template
        self.validator = Validator(rulebook=rulebook) if rulebook else Validator()
        self.verbose = verbose

    async def chat(
        self,
        instruction=None,
        context=None,
        system=None,
        sender=None,
        recipient=None,
        branch=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        clear_messages=False,
        use_annotation=True,
        return_branch=False,
        **kwargs,
    ):
        """
        Asynchronously performs a chat operation.

        Args:
            instruction (str, optional): Instruction message.
            context (str, optional): Context message.
            system (str, optional): System message.
            sender (str, optional): Sender identifier.
            recipient (str, optional): Recipient identifier.
            branch (Branch, optional): Branch instance.
            requested_fields (list, optional): Fields requested in the response.
            form (Form, optional): Form data.
            tools (bool, optional): Flag indicating if tools should be used.
            invoke_tool (bool, optional): Flag indicating if tools should be invoked.
            return_form (bool, optional): Flag indicating if form should be returned.
            strict (bool, optional): Flag indicating if strict validation should be applied.
            rulebook (Rulebook, optional): Rulebook instance for validation.
            imodel (iModel, optional): Model instance.
            clear_messages (bool, optional): Flag indicating if messages should be cleared.
            use_annotation (bool, optional): Flag indicating if annotations should be used.
            return_branch (bool, optional): Flag indicating if branch should be returned.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response.
        """
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(
            self._chat,
            instruction=instruction,
            context=context,
            system=system,
            sender=sender,
            recipient=recipient,
            branch=branch,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            clear_messages=clear_messages,
            use_annotation=use_annotation,
            return_branch=return_branch,
            **kwargs,
        )

    async def direct(
        self,
        instruction=None,
        *,
        context=None,
        form=None,
        branch=None,
        tools=None,
        return_branch=False,
        reason: bool = False,
        predict: bool = False,
        score=None,
        select=None,
        plan=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        directive: str = None,
        verbose=None,
        **kwargs,
    ):
        """
        Asynchronously directs the operation based on the provided parameters.

        Args:
            instruction (str, optional): Instruction message.
            context (str, optional): Context message.
            form (Form, optional): Form data.
            branch (Branch, optional): Branch instance.
            tools (Any, optional): Tools to be used.
            return_branch (bool, optional): Flag indicating if branch should be returned.
            reason (bool, optional): Flag indicating if reason should be included.
            predict (bool, optional): Flag indicating if prediction should be included.
            score (Any, optional): Score parameters.
            select (Any, optional): Select parameters.
            plan (Any, optional): Plan parameters.
            allow_action (bool, optional): Flag indicating if action should be allowed.
            allow_extension (bool, optional): Flag indicating if extension should be allowed.
            max_extension (int, optional): Maximum extension value.
            confidence (Any, optional): Confidence parameters.
            score_num_digits (int, optional): Number of digits for score.
            score_range (tuple, optional): Range for score.
            select_choices (list, optional): Choices for selection.
            plan_num_step (int, optional): Number of steps for plan.
            predict_num_sentences (int, optional): Number of sentences for prediction.
            directive (str, optional): Directive for the operation.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response.
        """
        kwargs = {**retry_kwargs, **kwargs}
        verbose = verbose if verbose is not None else self.verbose

        if not directive:

            out = await rcall(
                self._direct,
                instruction=instruction,
                context=context,
                form=form,
                branch=branch,
                tools=tools,
                return_branch=return_branch,
                reason=reason,
                predict=predict,
                score=score,
                select=select,
                plan=plan,
                allow_action=allow_action,
                allow_extension=allow_extension,
                max_extension=max_extension,
                confidence=confidence,
                score_num_digits=score_num_digits,
                score_range=score_range,
                select_choices=select_choices,
                plan_num_step=plan_num_step,
                predict_num_sentences=predict_num_sentences,
                verbose=verbose,
                **kwargs,
            )

            if verbose:
                print(
                    "\n--------------------------------------------------------------"
                )
                print(f"Directive successfully completed!")

            return out

        out = await rcall(
            self._mono_direct,
            directive=directive,
            instruction=instruction,
            context=context,
            branch=branch,
            tools=tools,
            verbose=verbose,
            **kwargs,
        )

        if verbose:
            print("--------------------------------------------------------------")
            print(f"Directive successfully completed!")

        return out
