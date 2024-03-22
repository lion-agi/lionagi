from typing import Any

from lionagi.libs import ln_convert as convert
from lionagi.libs.ln_async import AsyncUtil

from lionagi.core.messages.schema import Instruction
from lionagi.core.branch.branch import Branch

from lionagi.core.flow.base.baseflow import BasePolyFlow


class PolyChat(BasePolyFlow):

    def __init__(self, session) -> None:
        super().__init__(session)

    async def parallel_chat(
        self,
        instruction: Instruction | str,
        num_instances=1,
        context=None,
        sender=None,
        branch_system=None,
        messages=None,
        tools=False,
        out=True,
        invoke: bool = True,
        output_fields=None,
        persist_path=None,
        branch_config=None,
        explode=False,
        **kwargs,
    ) -> Any:
        """
        parallel chat
        """

        if branch_config is None:
            branch_config = {}
        return await self._parallel_chat(
            instruction,
            num_instances=num_instances,
            context=context,
            sender=sender,
            branch_system=branch_system,
            messages=messages,
            tools=tools,
            out=out,
            invoke=invoke,
            output_fields=output_fields,
            persist_path=persist_path,
            branch_config=branch_config,
            explode=explode,
            **kwargs,
        )

    async def _parallel_chat(
        self,
        instruction: Instruction | str,
        num_instances=1,
        context=None,
        sender=None,
        messages=None,
        tools=False,
        out=True,
        invoke: bool = True,
        output_fields=None,
        persist_path=None,
        branch_config={},
        explode=False,
        include_mapping=True,
        default_key="response",
        **kwargs,
    ) -> Any:
        """
        parallel chat
        """

        branches = {}

        async def _inner(i, ins_, cxt_):

            branch_ = Branch(
                messages=messages,
                service=self.session.default_branch.service,
                llmconfig=self.session.default_branch.llmconfig,
                persist_path=persist_path,
                **branch_config,
            )

            branch_.branch_name = branch_.id_

            if tools:
                branch_.tool_manager = self.session.default_branch.tool_manager

            res_ = await branch_.chat(
                instruction=ins_ or instruction,
                context=cxt_ or context,
                sender=sender,
                tools=tools,
                invoke=invoke,
                out=out,
                output_fields=output_fields,
                **kwargs,
            )

            branches[branch_.id_] = branch_
            if include_mapping:
                return {
                    "instruction": ins_ or instruction,
                    "context": cxt_ or context,
                    "branch_id": branch_.id_,
                    default_key: res_,
                }

            else:
                return res_

        async def _inner_2(i, ins_=None, cxt_=None):
            """returns num_instances of branches performing for same task/context"""
            tasks = [_inner(i, ins_, cxt_) for _ in range(num_instances)]
            ress = await AsyncUtil.execute_tasks(*tasks)
            return convert.to_list(ress)

        async def _inner_3(i):
            """different instructions but same context"""
            tasks = [_inner_2(i, ins_=ins_) for ins_ in convert.to_list(instruction)]
            ress = await AsyncUtil.execute_tasks(*tasks)
            return convert.to_list(ress)

        async def _inner_3_b(i):
            """different context but same instruction"""
            tasks = [_inner_2(i, cxt_=cxt_) for cxt_ in convert.to_list(context)]
            ress = await AsyncUtil.execute_tasks(*tasks)
            return convert.to_list(ress)

        async def _inner_4(i):
            """different instructions and different context"""

            tasks = []
            if explode:
                tasks = [
                    _inner_2(i, ins_=ins_, cxt_=cxt_)
                    for ins_ in convert.to_list(instruction)
                    for cxt_ in convert.to_list(context)
                ]
            else:
                tasks = [
                    _inner_2(i, ins_=ins_, cxt_=cxt_)
                    for ins_, cxt_ in zip(
                        convert.to_list(instruction), convert.to_list(context)
                    )
                ]

            ress = await AsyncUtil.execute_tasks(*tasks)
            return convert.to_list(ress)

        if len(convert.to_list(instruction)) == 1:
            if len(convert.to_list(context)) == 1:
                out_ = await _inner_2(0)
                self.session.branches.update(branches)
                return out_

            elif len(convert.to_list(context)) > 1:
                out_ = await _inner_3_b(0)
                self.session.branches.update(branches)
                return out_

        elif len(convert.to_list(instruction)) > 1:
            if len(convert.to_list(context)) == 1:
                out_ = await _inner_3(0)
                self.session.branches.update(branches)
                return out_

            elif len(convert.to_list(context)) > 1:
                out_ = await _inner_4(0)
                self.session.branches.update(branches)
                return out_
