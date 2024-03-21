from lionagi.core.messages.schema import Instruction
from lionagi.core.schema.base_node import Tool
from .chat import MonoChat


class MonoFollowup(MonoChat):

    async def followup(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        max_followup: int = 1,
        auto=False,
        followup_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ):
        return await self._followup(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            auto=auto,
            followup_prompt=followup_prompt,
            output_prompt=output_prompt,
            out=out,
            **kwargs,
        )

    @staticmethod
    def _get_prompt(prompt=None, default=None, num_followup=None, instruction=None):
        if prompt is not None:
            return prompt

        try:
            try:
                return default.format(num_followup=num_followup)
            except Exception:
                return default.format(instruction=instruction)
        except Exception:
            return default

    def _create_followup_config(self, tools, **kwargs):

        if tools is not None and (
            isinstance(tools, list) and isinstance(tools[0], Tool)
        ):
            self.branch.tool_manager.register_tools(tools)

        if not self.branch.tool_manager.has_tools:
            raise ValueError("No tools found, You need to register tools")

        config = self.branch.tool_manager.parse_tool(tools=True, **kwargs)
        config["tool_parsed"] = True
        config["tool_choice"] = "auto"
        return config

    async def _handle_auto(
        self,
        _out=None,
        out=None,
        instruction=None,
        output_prompt=None,
        sender=None,
        output=False,
        **kwargs,
    ):
        if self.branch._is_invoked():
            return False

        if output:
            return await self._handle_auto_output(
                instruction, output_prompt, sender, out, **kwargs
            )
        return self._handle_auto_followup(_out, out)

    def _handle_auto_followup(self, _out, out):
        return _out if out else None

    async def _handle_auto_output(
        self, instruction, output_prompt, sender, out, **kwargs
    ):
        prompt = self._get_prompt(
            prompt=output_prompt, default=_output_prompt, instruction=instruction
        )
        return await self.chat(
            prompt, sender=sender, tool_parsed=True, out=out, **kwargs
        )

    async def _followup(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        max_followup: int = 1,
        auto=False,
        followup_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ) -> None:
        _out = ""
        config = self._create_followup_config(tools, **kwargs)

        i = 0
        while i < max_followup:

            prompt_ = self._get_prompt(
                prompt=followup_prompt,
                default=_followup_prompt,
                num_followup=max_followup - i,
            )

            if i == 0:

                prompt_ = {"notice": prompt_, "task": instruction}
                _out = await self.chat(
                    prompt_, context=context, system=system, sender=sender, **config
                )

            elif i > 0:
                _out = await self.chat(prompt_, sender=sender, **config)

                if auto:
                    a = self._handle_auto(_out=_out, out=out)
                    if a is not False:
                        return a

            i += 1

        if auto:
            a = await self._handle_auto(
                instruction,
                output_prompt=output_prompt,
                sender=sender,
                out=out,
                output=True,
                **kwargs,
            )
            if a:
                return a

        return _out


_followup_prompt = """In the current task you are allowed a maximum of another {num_steps} followup chats. if further actions are needed, invoke tools usage. If you are done, present the final result 
to user without further tool usage
"""

_output_prompt = (
    "notice: present final output to user, original user instruction: {instruction}"
)
