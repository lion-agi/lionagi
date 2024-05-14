from lionagi.libs.ln_func_call import rcall, alcall
from ..branch.branch import Branch

from .template._default_templates import PlanTemplate
from .chat import Chat


class Predict(Chat):

    async def predict(
        self,
        system=None,
        instruction=None,
        context=None,
        sender=None,
        recipient=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        out=True,
        **kwargs,
    ):

        self.branch.messages.clear()
        return await self.chat(
            system=system,
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            out=out,
            **kwargs,
        )


class Plan(Chat):

    default_template = PlanTemplate

    async def plan(
        self,
        system=None,  # system node - JSON serializable
        instruction=None,  # Instruction node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        form=None,
        tools=False,
        invoke_tool=True,
        out=True,
        **kwargs,
    ): ...

    async def _plan(
        self,
        *,
        instruction=None,
        branch=None,
        confidence_score=False,
        reason=False,
        retries=2,
        delay=0.5,
        backoff_factor=2,
        default_value=None,
        timeout=None,
        branch_name=None,
        system=None,
        messages=None,
        service=None,
        sender=None,
        llmconfig=None,
        tools=None,
        datalogger=None,
        persist_path=None,
        tool_manager=None,
        return_branch=False,
        **kwargs,
    ):

        instruction = instruction or ""

        branch = branch or Branch(
            name=branch_name,
            system=system,
            messages=messages,
            service=service,
            sender=sender,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            tool_manager=tool_manager,
        )

        _template = PlanTemplate(
            sentence=sentence,
            instruction=instruction,
            confidence_score=confidence_score,
            reason=reason,
        )

        await rcall(
            branch.chat,
            form=_template,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default_value,
            timeout=timeout,
            **kwargs,
        )

        _template.plan = fuzzy_parse_json(_template.plan)

        return (_template, branch) if return_branch else _template

    async def plan(
        sentence,
        *,
        instruction=None,
        num_instances=1,
        branch=None,
        confidence_score=False,
        reason=False,
        retries=2,
        delay=0.5,
        backoff_factor=2,
        default_value=None,
        timeout=None,
        branch_name=None,
        system=None,
        messages=None,
        service=None,
        sender=None,
        llmconfig=None,
        tools=None,
        datalogger=None,
        persist_path=None,
        tool_manager=None,
        return_branch=False,
        **kwargs,
    ):
        async def _inner(i=0):
            return await _plan(
                sentence=sentence,
                instruction=instruction,
                branch=branch,
                confidence_score=confidence_score,
                reason=reason,
                retries=retries,
                delay=delay,
                backoff_factor=backoff_factor,
                default_value=default_value,
                timeout=timeout,
                branch_name=branch_name,
                system=system,
                messages=messages,
                service=service,
                sender=sender,
                llmconfig=llmconfig,
                tools=tools,
                datalogger=datalogger,
                persist_path=persist_path,
                tool_manager=tool_manager,
                return_branch=return_branch,
                **kwargs,
            )

        if num_instances == 1:
            return await _inner()

        elif num_instances > 1:
            return await alcall(range(num_instances), _inner)
