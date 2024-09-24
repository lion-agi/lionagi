"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Module for the UnitProcessor class in the Lion framework.

This module provides the UnitProcessor class, which encapsulates various
processing methods for units, including act, action request, chat, direct,
and validation processing.
"""

from functools import partial
from typing import Callable, Any, Literal
from lion_core.abc import BaseProcessor
from lion_core.imodel.imodel import iModel
from lion_core.generic.progression import Progression
from lion_core.form.base import BaseForm
from lion_core.rule.rule_processor import RuleProcessor
from lion_core.form.form import Form
from lion_core.unit.unit_form import UnitForm
from lion_core.unit.process_act import process_action
from lion_core.unit.process_action_request import process_action_request
from lion_core.unit.process_action_response import process_action_response
from lion_core.unit.process_chat import process_chat
from lion_core.unit.process_direct import process_direct
from lion_core.unit.process_rule import process_rule
from lion_core.unit.process_completion import fallback_structure_model_response

from lion_core.libs import rcall
from lion_core.setting import LN_UNDEFINED
from lion_core.session.branch import Branch
from lion_core.rule.rulebook import RuleBook


class Unit(BaseProcessor):
    """
    Unit processor class for handling various processing tasks.

    This class provides methods for processing acts, action requests, chats,
    direct interactions, and validations within a branch context.

    Attributes:
        default_form (Type[Form]): The default form type to use.
        branch (Branch): The branch associated with this processor.
    """

    def __init__(
        self,
        branch: "Branch",
        imodel: iModel = None,
        structure_str: bool = False,
        fallback_structure: Callable | None = None,
        fallback_imodel: iModel | None = None,
        **kwargs,
    ):
        """
        Initialize the UnitProcessor.

        Args:
            branch (Branch): The branch to associate with this processor.

        kwargs for fallback_structure function

        """
        self.branch = branch
        self.imodel = imodel or branch.imodel
        self.structure_str = structure_str
        if structure_str:
            if not fallback_structure:
                self.fallback_structure = partial(
                    fallback_structure_model_response,
                    imodel=fallback_imodel or self.imodel,
                    **kwargs,
                )
            else:
                self.fallback_structure = partial(fallback_structure, **kwargs)

    async def process_action_request(
        self,
        response: dict | None = None,
        action_request=None,
        invoke_action: bool = True,
    ) -> list | None:
        return await process_action_request(
            branch=self.branch,
            response=response,
            action_request=action_request,
            invoke_action=invoke_action,
        )

    async def process_action_response(
        self,
        action_requests: list,
        responses: list,
        response_parser: Callable = None,
        **kwargs: dict,
    ):
        await process_action_response(
            branch=self.branch,
            action_requests=action_requests,
            responses=responses,
            response_parser=response_parser,
            parser_kwargs=kwargs,
        )

    async def process_chat(
        self,
        instruction=None,
        *,
        guidance=None,
        context=None,
        system=None,
        sender=None,
        recipient=None,
        request_fields=None,
        form: Form = None,
        tools=False,
        images=None,
        image_detail=None,
        system_sender=None,
        model_config: dict | None = None,
        assignment: str = None,  # if use form, must provide assignment
        task_description: str = None,
        clear_messages: bool = False,
        imodel: iModel = None,
        costs: tuple = (0, 0),
        rule_processor: RuleProcessor = None,
        rulebook: RuleBook = None,
        return_branch: bool = False,
        progress: Progression = None,
        retries: int = 0,
        initial_delay: float = 0,
        delay: float = 0,
        backoff_factor: float = 1,
        default: Any = LN_UNDEFINED,
        timeout: float | None = 120,
        timing: bool = False,
        verbose_error: bool = True,
        error_msg: str | None = None,
        error_map: dict = None,
        **kwargs: Any,  # additional model parameters
    ):
        progress = progress or self.branch.progress

        retry_call = partial(
            rcall,
            default=default,
            timeout=timeout,
            timing=timing,
            verbose=verbose_error,
            error_msg=error_msg,
            error_map=error_map,
            retries=retries,
            initial_delay=initial_delay,
            delay=delay,
            backoff_factor=backoff_factor,
        )

        return await retry_call(
            process_chat,
            system_sender=system_sender,
            branch=self.branch,
            instruction=instruction,
            context=context,
            form=form,
            sender=sender,
            recipient=recipient,
            request_fields=request_fields,
            system=system,
            guidance=guidance,
            tools=tools,
            images=images,
            image_detail=image_detail,
            model_config=model_config,
            assignment=assignment,
            task_description=task_description,
            clear_messages=clear_messages,
            imodel=imodel,
            progress=progress,
            costs=costs,
            rule_processor=rule_processor,
            rulebook=rulebook,
            return_branch=return_branch,
            structure_str=self.structure_str,
            fallback_structure=self.fallback_structure,
            **kwargs,
        )

    async def process_action(
        self,
        form: UnitForm,
        actions: dict,
        handle_unmatched: Literal["ignore", "raise", "remove", "force"] = "force",
        return_branch: bool = False,
        invoke_action: bool = True,
        action_response_parser: Callable = None,
        action_parser_kwargs: dict = None,
    ):
        return await process_action(
            branch=self.branch,
            form=form,
            actions=actions,
            return_branch=return_branch,
            handle_unmatched=handle_unmatched,
            invoke_action=invoke_action,
            action_response_parser=action_response_parser,
            action_parser_kwargs=action_parser_kwargs,
        )

    async def process_rule(
        self,
        form: BaseForm,
        rule_processor: RuleProcessor | None = None,  # priority 1
        response: dict | str = None,
        rulebook: Any = None,
        strict_validation: bool = False,
    ):
        return await process_rule(
            form=form,
            rule_processor=rule_processor,
            response_=response,
            rulebook=rulebook,
            strict=strict_validation,
            structure_str=self.structure_str,
            fallback_structure=self.fallback_structure,
        )

    async def process_direct(
        self,
        instruction: str | str = None,
        *,
        form: UnitForm | None,
        context: Any = None,
        guidance: str = LN_UNDEFINED,
        reason: bool = False,
        confidence: bool = False,
        plan: bool = False,
        reflect: bool = False,
        tool_schema: list = None,
        invoke_tool: bool = None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        tools: Any | None = None,
        return_branch=False,
        chain_plan=False,
        progress: Progression = None,
        retries: int = 0,
        initial_delay: float = 0,
        delay: float = 0,
        backoff_factor: float = 1,
        default: Any = LN_UNDEFINED,
        timeout: float | None = 120,
        timing: bool = False,
        verbose_error: bool = True,
        error_msg: str | None = None,
        error_map: dict = None,
        **kwargs: Any,  # additional _direct kwargs
    ):
        progress = progress or self.branch.progress

        retry_call = partial(
            rcall,
            default=default,
            timeout=timeout,
            timing=timing,
            verbose=verbose_error,
            error_msg=error_msg,
            error_map=error_map,
            retries=retries,
            initial_delay=initial_delay,
            delay=delay,
            backoff_factor=backoff_factor,
        )

        return await retry_call(
            process_direct,
            branch=self.branch,
            instruction=instruction,
            form=form,
            context=context,
            guidance=guidance,
            reason=reason,
            confidence=confidence,
            plan=plan,
            reflect=reflect,
            tool_schema=tool_schema,
            invoke_tool=invoke_tool,
            allow_action=allow_action,
            allow_extension=allow_extension,
            max_extension=max_extension,
            tools=tools,
            return_branch=return_branch,
            chain_plan=chain_plan,
            progress=progress,
            **kwargs,
        )
