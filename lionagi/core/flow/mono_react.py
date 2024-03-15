from .mono_chat import MonoChat
from lionagi.core.schema.base_node import Tool
from lionagi.core.messages.schema import Instruction


class MonoReAct(MonoChat):

    async def ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        **kwargs,
    ):
        return await self._ReAct(
            instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            num_rounds=num_rounds,
            reason_prompt=reason_prompt,
            action_prompt=action_prompt,
            output_prompt=output_prompt,
            **kwargs,
        )

    @staticmethod
    def _get_prompt(prompt=None, default=None, num_steps=None, instruction=None):
        if prompt is not None:
            return prompt

        try:
            try:
                return default.format(num_steps=num_steps)
            except:
                return default.format(instruction=instruction)
        except:
            return default

    def _create_followup_config(self, tools, **kwargs):

        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
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
        config=None,
    ):
        if not self.branch._is_invoked():
            if output:
                return await self._handle_auto_output(
                    instruction, output_prompt, sender, out, config
                )
            return self._handle_auto_followup(_out, out)
        return False

    def _handle_auto_followup(self, _out, out):
        return _out if out else None

    async def _handle_auto_output(
        self, instruction, output_prompt, sender, out, config
    ):
        prompt_ = self._get_prompt(
            output_prompt, _output_prompt, instruction=instruction
        )
        return await self.chat(prompt_, sender=sender, **config)

    async def _ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        auto=False,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ):

        config = self._create_followup_config(tools, **kwargs)

        i = 0
        while i < num_rounds:
            prompt_ = self._get_prompt(
                reason_prompt, _reason_prompt, (num_rounds - i) * 2
            )
            instruct = {"Notice": prompt_}

            # reason
            if i == 0:
                instruct["Task"] = instruction

                await self.chat(
                    instruct,
                    context=context,
                    system=system,
                    sender=sender,
                    **kwargs,
                )

            elif i > 0:
                await self.chat(instruct, sender=sender, **kwargs)

            # action
            prompt_ = self._get_prompt(
                action_prompt, _action_prompt, (num_rounds - i) * 2 - 1
            )
            _out = await self.chat(prompt_, sender=sender, **config)

            if auto:
                a = await self._handle_auto(_out=_out, out=out)
                if a:
                    return a

            i += 1

        if auto:
            a = await self._handle_auto(
                instruction,
                output_prompt=output_prompt,
                sender=sender,
                out=out,
                output=True,
                config=config,
            )
            if a:
                return a

    # TODO: auto_ReAct


_reason_prompt = """
you have {num_steps} step left in current task. if available, integrate previous tool responses. perform reasoning and prepare action plan according to available tools only, apply divide and conquer technique.
"""

_action_prompt = """
you have {num_steps} step left in current task, if further actions are needed, invoke tools usage. If you are done, present the final result to user without further tool usage
"""
_output_prompt = (
    "notice: present final output to user, original user instruction: {instruction}"
)
