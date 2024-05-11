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
