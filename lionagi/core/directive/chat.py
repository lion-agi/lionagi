from .base import BaseDirective


class Chat(BaseDirective):

    async def chat(
        self,
        instruction=None,  # Instruction node - JSON serializable
        *,
        system=None,  # system node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        validator=None,
        imodel=None,
        **kwargs,
    ):

        config = self._create_chat_config(
            system=system,
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            **kwargs,
        )

        payload, completion = await self._call_chatcompletion(imodel=imodel, **config)

        return await self._output(
            payload=payload,
            completion=completion,
            sender=sender,
            invoke_tool=invoke_tool,
            requested_fields=requested_fields,
            form=form,
            return_form=return_form,
            strict=strict,
            validator=validator,
        )
