from typing import Any

from lionagi.core.flow.base_flow import BasePolyFlow
from lionagi.core.message.schema import Instruction
from lionagi.core.session.branch import Branch
from lionagi.libs import ln_convert as convert
from lionagi.libs import ln_func_call as func_call
from lionagi.libs.ln_async import AsyncUtil


class PolyChat(BasePolyFlow):

    def __init__(self, session) -> None:
        super().__init__(session)

    async def _parallel_chat(
        self,
        instruction: Instruction | str,
        num_instances=1,
        prefix="branch",
        context=None,
        sender=None,
        branch_system=None,
        messages=None,
        tools=False,
        out=True,
        invoke: bool = True,
        persist_path=None,
        branch_config={},
        explode=False,
        **kwargs,
    ) -> Any:
        """
        use num_instances to run through same instruction in num_instances of branches
        concurrently.
        """

        async def _inner(
            instruction=instruction,
            context=context,
            sender=sender,
            branch_system=branch_system,
        ):
            branch_name = f"{prefix}_{i}"
            if branch_name in self.session.branches:
                while branch_name in self.session.branches:
                    i += 1
                    branch_name = f"{prefix}_{i}"

            branch_ = Branch(
                branch_name=branch_name,
                system=branch_system,
                messages=messages,
                service=self.session.default_branch.service,
                llmconfig=self.session.default_branch.llmconfig,
                persist_path=persist_path,
                **branch_config,
            )

            if tools:
                branch_.tool_manager = self.session.default_branch.tool_manager

            res_ = await branch_.chat(
                instruction=instruction,
                context=context,
                sender=sender,
                system=branch_system,
                tools=tools,
                invoke=invoke,
                **kwargs,
            )

            self.session.take_branch(branch_)
            return res_

        async def _inner_2(
            instruction=instruction,
            context=context,
            sender=sender,
            branch_system=branch_system,
        ):
            """returns num_instances of branches performing for same task/context"""
            ress = await func_call.alcall(
                [i for i in range(num_instances)],
                _inner,
                instruction=instruction,
                context=context,
                sender=sender,
                branch_system=branch_system,
            )
            return ress

        async def _inner_3(
            instruction=instruction,
            context=context,
            sender=sender,
            branch_system=branch_system,
        ):
            """different instructions but same context"""
            ress = await func_call.alcall(
                instruction,
                _inner_2,
                context=context,
                sender=sender,
                branch_system=branch_system,
            )
            return ress

        async def _inner_3_b(
            instruction=instruction,
            context=context,
            sender=sender,
            branch_system=branch_system,
        ):
            """different context but same instruction"""
            tasks = [
                _inner_2(instruction, i, sender=sender, branch_system=branch_system)
                for i in convert.to_list(context)
            ]
            ress = await AsyncUtil.execute_tasks(*tasks)
            return ress

        async def _inner_4(
            instruction,
            context=context,
            sender=sender,
            branch_system=branch_system,
            explode=explode,
        ):
            """different instructions and different context"""

            _f = lambda x: _inner_3(
                x, context=context, sender=sender, branch_system=branch_system
            )
            _fs = func_call.lcall(instruction, _f)
            ress = await func_call.mcall(context, _fs, explode=explode)

            return ress

        if len(convert.to_list(instruction)) == 1:
            if len(convert.to_list(context)) == 1:
                return await _inner_2(
                    instruction,
                    context=context,
                    sender=sender,
                    branch_system=branch_system,
                )

            elif len(convert.to_list(context)) > 1:
                return await _inner_3_b(
                    instruction,
                    context=context,
                    sender=sender,
                    branch_system=branch_system,
                )

        elif len(convert.to_list(instruction)) > 1:
            if len(convert.to_list(context)) == 1:
                return await _inner_3(
                    instruction,
                    context=context,
                    sender=sender,
                    branch_system=branch_system,
                )
            elif len(convert.to_list(context)) > 1:
                return await _inner_4(
                    instruction,
                    context=context,
                    sender=sender,
                    branch_system=branch_system,
                )

    async def _parallel_instruct(self): ...


class PolyEval(PolyChat):

    def __init__(self, session) -> None:
        super().__init__(session)

    async def check_score(context):
        async def _inner(i):
            session = Session(system=scor_sys, service=service)
            return await session.chat(
                instruction=instruction, context=context, model="gpt-3.5-turbo"
            )

        scores = await func_call.alcall([i for i in range(2)], _inner)

        z = []
        for i in scores:
            try:
                a = convert.to_num(i)
                z.append(a)
            except:
                pass


class DynamicPolyFlow(PolyChat): ...
