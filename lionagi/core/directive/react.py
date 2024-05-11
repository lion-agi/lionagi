# async def _react(
#     sentence=None,
#     *,
#     instruction=None,
#     branch=None,
#     confidence_score=False,
#     retries=2,
#     delay=0.5,
#     backoff_factor=2,
#     default_value=None,
#     timeout=None,
#     branch_name=None,
#     system=None,
#     messages=None,
#     service=None,
#     sender=None,
#     llmconfig=None,
#     tools=None,
#     datalogger=None,
#     persist_path=None,
#     tool_manager=None,
#     return_branch=False,
#     **kwargs,
# ):

#     if "temperature" not in kwargs:
#         kwargs["temperature"] = 0.1

#     instruction = instruction or ""

#     if branch and tools:
#         _process_tools(tools, branch)

#     branch = branch or Branch(
#         name=branch_name,
#         system=system,
#         messages=messages,
#         service=service,
#         sender=sender,
#         llmconfig=llmconfig,
#         tools=tools,
#         datalogger=datalogger,
#         persist_path=persist_path,
#         tool_manager=tool_manager,
#     )

#     _template = ReactTemplate(
#         sentence=sentence,
#         instruction=instruction,
#         confidence_score=confidence_score,
#     )

#     await func_call.rcall(
#         branch.chat,
#         form=_template,
#         retries=retries,
#         delay=delay,
#         backoff_factor=backoff_factor,
#         default=default_value,
#         timeout=timeout,
#         **kwargs,
#     )

#     if _template.action_needed:
#         actions = _template.actions
#         tasks = [branch.tool_manager.invoke(i.values()) for i in actions]
#         results = await AsyncUtil.execute_tasks(*tasks)

#         a = []
#         for idx, item in enumerate(actions):
#             res = {
#                 "function": item["function"],
#                 "arguments": item["arguments"],
#                 "output": results[idx],
#             }
#             branch.add_message(response=res)
#             a.append(res)

#         _template.__setattr__("action_response", a)

#     return (_template, branch) if return_branch else _template


# async def react(
#     sentence=None,
#     *,
#     instruction=None,
#     num_instances=1,
#     branch=None,
#     confidence_score=False,
#     retries=2,
#     delay=0.5,
#     backoff_factor=2,
#     default_value=None,
#     timeout=None,
#     branch_name=None,
#     system=None,
#     messages=None,
#     service=None,
#     sender=None,
#     llmconfig=None,
#     tools=None,
#     datalogger=None,
#     persist_path=None,
#     tool_manager=None,
#     return_branch=False,
#     **kwargs,
# ):

#     async def _inner(i=0):
#         return await _react(
#             sentence=sentence,
#             instruction=instruction,
#             num_instances=num_instances,
#             branch=branch,
#             confidence_score=confidence_score,
#             retries=retries,
#             delay=delay,
#             backoff_factor=backoff_factor,
#             default_value=default_value,
#             timeout=timeout,
#             branch_name=branch_name,
#             system=system,
#             messages=messages,
#             service=service,
#             sender=sender,
#             llmconfig=llmconfig,
#             tools=tools,
#             datalogger=datalogger,
#             persist_path=persist_path,
#             tool_manager=tool_manager,
#             return_branch=return_branch,
#             **kwargs,
#         )

#     if num_instances == 1:
#         return await _inner()

#     elif num_instances > 1:
#         return await func_call.alcall(range(num_instances), _inner)


from typing import Callable
from lionagi.core.flow.monoflow.chat import MonoChat
from lionagi.core.tool import Tool
from lionagi.core.messages.schema import Instruction


class MonoReAct(MonoChat):

    REASON_PROMPT = """
    You have {num_steps} steps left in the current task. If available, integrate previous tool responses.
    Perform reasoning and prepare an action plan according to available tools only. Apply divide and conquer technique.
    """

    ACTION_PROMPT = """
    You have {num_steps} steps left in the current task. invoke tool usage.
    """

    OUTPUT_PROMPT = "Notice: Present the final output to the user. Original user instruction: {instruction}"

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
            if num_steps is not None:
                return default.format(num_steps=num_steps)
            elif instruction is not None:
                return default.format(instruction=instruction)
        except (KeyError, ValueError):
            pass

        return default

    def _create_followup_config(self, tools, tool_choice="auto", **kwargs):
        if tools and isinstance(tools, list) and isinstance(tools[0], (Callable, Tool)):
            self.branch.tool_manager.register_tools(tools)

        if not self.branch.tool_manager.has_tools:
            raise ValueError("No tools found. You need to register tools.")

        if tools is None:
            tools = True
        config = self.branch.tool_manager.parse_tool(tools=tools, **kwargs)
        config["tool_parsed"] = True
        config["tool_choice"] = tool_choice
        return config

    async def _ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        auto=True,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ):
        config = self._create_followup_config(tools, **kwargs)
        kwargs.pop("tools", None)

        i = 0
        _out = ""

        while i < num_rounds:
            _prompt = self._get_prompt(
                prompt=reason_prompt,
                default=self.REASON_PROMPT,
                num_steps=(num_rounds - i) * 2,
            )
            _instruct = {"NOTICE": _prompt}

            # reason
            if i == 0:
                _instruct["TASK"] = instruction

                await self.chat(
                    _instruct, context=context, sender=sender, system=system, **kwargs
                )

            elif i > 0:
                await self.chat(_instruct, sender=sender, **kwargs)

            # action
            _prompt = self._get_prompt(
                prompt=action_prompt,
                default=self.ACTION_PROMPT,
                num_steps=(num_rounds - i) * 2 - 1,
            )

            _out = await self.chat(_prompt, sender=sender, **config)

            if not self.branch._is_invoked():
                return _out if out else None

            i += 1

        if not self.branch._is_invoked():
            return _out if out else None

        _prompt = self._get_prompt(
            prompt=output_prompt,
            default=self.OUTPUT_PROMPT,
            instruction=instruction,
        )
        _out = await self.chat(_prompt, sender=sender, **kwargs)
        return _out if out else None
