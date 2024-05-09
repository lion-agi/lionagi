from .base import BaseDirective


class Chat(BaseDirective):

    async def chat(
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

        payload, completion = await self._call_chatcompletion(**config)
        await self._process_chatcompletion(payload, completion, sender)
        
        return await self._output(
            invoke_tool=invoke_tool,
            out=out,
            requested_fields=requested_fields,
            form=form,
        )
