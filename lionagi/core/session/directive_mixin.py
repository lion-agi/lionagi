# lionagi/core/session/directive_mixin.py
import warnings

from lion_core.session import Branch
from pydantic import BaseModel

from lionagi.core.unit import Unit

from ..message.action_response import ActionResponse


async def chat(
    self: Branch,
    instruction=None,  # additional instruction
    guidance=None,
    context=None,  # context to perform the instruction on
    system=None,  # optionally swap system message
    sender=None,  # sender of the instruction, default "user"
    recipient=None,  # recipient of the instruction, default "branch.ln_id"
    request_fields=None,
    form=None,  # form to create instruction from, default None,
    tools=False,  # the tools to use, use True to consider all tools, no tools by default
    invoke_tool=True,  # whether to invoke the tool when function calling, default True
    return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
    imodel=None,  # the optinally swappable iModel for the commands, otherwise self.branch.imodel
    clear_messages=False,
    request_model: type[BaseModel] = None,
    images=None,
    image_detail=None,
    image_path=None,
    num_parse_retries: int = 0,
    retry_imodel=None,
    retry_kwargs: dict = {},
    handle_validation="raise",
    skip_validation: bool = False,
    invoke_action: bool = True,
    **kwargs,
):
    if "requested_fields" in kwargs:
        warnings.warn(
            message=(
                "Since v0.3.0, `requested_fields` is deprecated, use `request_fields` instead."
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        request_fields = request_fields or kwargs["requested_fields"]
        kwargs.pop("requested_fields", None)

    if "strict" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `strict` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )

    if "use_annotation" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `use_annotation` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        use_annotation = use_annotation or kwargs["use_annotation"]
        kwargs.pop("use_annotation", None)

    if "rulebook" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `rulebook` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        rulebook = rulebook or kwargs["rulebook"]
        kwargs.pop("rulebook", None)

    if "pydantic_model" in kwargs:
        warnings.warn(
            message=(
                "Since v0.3.0, `pydantic_model` is deprecated, use `request_model` instead."
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        pydantic_model = pydantic_model or kwargs["pydantic_model"]
        kwargs.pop("pydantic_model", None)

    if "return_pydantic_model" in kwargs:
        warnings.warn(
            message=(
                "Since v0.3.0, `return_pydantic_model` is deprecated, if you use a request model, chat will return a pydantic model by default."
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        return_form = return_form or kwargs["return_pydantic_model"]
        kwargs.pop("return_pydantic_model", None)

    if "retries" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `retries` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        retries = retries or kwargs["retries"]
        kwargs.pop("retries", None)

    if "delay" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `delay` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        delay = delay or kwargs["delay"]
        kwargs.pop("delay", None)

    if "backoff_factor" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `backoff_factor` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        backoff_factor = backoff_factor or kwargs["backoff_factor"]
        kwargs.pop("backoff_factor", None)

    if "default" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `default` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        default = default or kwargs["default"]
        kwargs.pop("default", None)

    if "timeout" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `timeout` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        timeout = timeout or kwargs["timeout"]
        kwargs.pop("timeout", None)

    if "timing" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `timing` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        timing = timing or kwargs["timing"]
        kwargs.pop("timing", None)

    if "template" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `template` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        template = template or kwargs["template"]
        kwargs.pop("template", None)

    if "verbose" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `verbose` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        verbose = verbose or kwargs["verbose"]
        kwargs.pop("verbose", None)

    if "formatter" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `formatter` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        formatter = formatter or kwargs["formatter"]
        kwargs.pop("formatter", None)

    if "format_kwargs" in kwargs:
        warnings.warn(
            message=("Since v0.3.0, `format_kwargs` is deprecated"),
            category=DeprecationWarning,
            stacklevel=2,
        )
        format_kwargs = format_kwargs or kwargs["format_kwargs"]
        kwargs.pop("format_kwargs", None)

    if not images and image_path:
        from lionagi.libs import ImageUtil

        images = ImageUtil.read_image_to_base64(image_path)

    output = await self.communicate(
        instruction=instruction,
        guidance=guidance,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        request_fields=request_fields,
        tools=tools,
        invoke_tool=invoke_tool,
        imodel=imodel,
        images=images,
        image_detail=image_detail,
        num_parse_retries=num_parse_retries,
        retry_imodel=retry_imodel,
        retry_kwargs=retry_kwargs,
        handle_validation=handle_validation,
        skip_validation=skip_validation,
        invoke_action=invoke_action,
        clear_messages=clear_messages,
        request_model=request_model,
        **kwargs,
    )

    return output


async def direct(
    self,
    *,
    instruction=None,
    context=None,
    form=None,
    tools=None,
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
    imodel=None,
    system=None,
    rulebook=None,
    directive=None,
    images=None,
    image_path=None,
    template=None,
    verbose=True,
    formatter=None,
    format_kwargs=None,
    **kwargs,
):
    """
    Asynchronously directs the operation based on the provided parameters.

    Args:
        instruction (str, optional): Instruction message.
        context (Any, optional): Context to perform the instruction on.
        form (Form, optional): Form data.
        tools (Any, optional): Tools to use.
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
        imodel (iModel, optional): Optionally swappable iModel for the commands.
        system (str, optional): Optionally swap the system message.
        rulebook (Any, optional): The rulebook to use for validation.
        directive (str, optional): Directive for the operation.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The processed response.

    Examples:
        >>> result = await self.direct(instruction="Process data", context={"data": "example"})
        >>> print(result)
    """
    if system:
        self.add_message(system=system)

    if not images and image_path:
        from lionagi.libs import ImageUtil

        images = ImageUtil.read_image_to_base64(image_path)

    _directive = Unit(
        self,
        imodel=imodel,
        rulebook=rulebook,
        verbose=verbose,
        formatter=formatter,
        format_kwargs=format_kwargs,
    )

    idx = len(self.progress)
    if directive and isinstance(directive, str):
        form = await _directive.direct(
            directive=directive,
            instruction=instruction,
            context=context,
            tools=tools,
            reason=reason,
            confidence=confidence,
            images=images,
            template=template,
            **kwargs,
        )

        action_responses = [
            i for i in self.messages[idx:] if isinstance(i, ActionResponse)
        ]
        if len(action_responses) > 0:
            _dict = {
                f"action_{idx}": i.content["action_response"]
                for idx, i in enumerate(action_responses)
            }
            if not hasattr(form, "action_response"):
                form.append_to_request("action_response", {})
            form.action_response.update(_dict)

        return form

    form = await _directive.direct(
        instruction=instruction,
        context=context,
        form=form,
        tools=tools,
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
        images=images,
        template=template,
        **kwargs,
    )

    action_responses = [
        i for i in self.messages[idx:] if isinstance(i, ActionResponse)
    ]
    if len(action_responses) > 0:
        _dict = {
            f"action_{idx}": i.content["action_response"]
            for idx, i in enumerate(action_responses)
        }
        if not hasattr(form, "action_response"):
            form.append_to_request("action_response", {})
        form.action_response.update(_dict)

    return form
