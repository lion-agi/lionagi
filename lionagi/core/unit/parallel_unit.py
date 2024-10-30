from lionagi.core.collections import iModel
from lionagi.core.collections.abc import Directive
from lionagi.core.session.branch import Branch
from lionagi.core.unit.util import retry_kwargs
from lionagi.core.validator.validator import Validator
from lionagi.libs import AsyncUtil, convert
from lionagi.libs.ln_func_call import rcall


class ParallelUnit(Directive):
    """
    A class representing a unit that can perform parallel chat interactions.

    Attributes:
        branch (Session): The session to which this ParallelUnit belongs.
        imodel (iModel): The model to be used for interactions.
        form_template (Form): The template for the form to be used.
        validator (Validator): The validator to validate the forms.

    Methods:
        pchat(*args, **kwargs): Asynchronously performs a parallel chat interaction.
        _parallel_chat(
            instruction,
            num_instances=1,
            context=None,
            sender=None,
            messages=None,
            tools=False,
            out=True,
            invoke=True,
            requested_fields=None,
            persist_path=None,
            branch_config={},
            explode=False,
            include_mapping=True,
            default_key="response",
            **kwargs,
        ): Asynchronously performs the core logic for parallel chat interactions.
    """

    default_template = None

    def __init__(
        self, session, imodel: iModel = None, template=None, rulebook=None
    ) -> None:
        """
        Initializes a new instance of ParallelUnit.

        Args:
            session (Session): The session to which this ParallelUnit belongs.
            imodel (iModel, optional): The model to be used for interactions.
            template (Form, optional): The template for the form to be used.
            rulebook (Rulebook, optional): The rulebook to validate the forms.
        """
        self.branch = session
        if imodel and isinstance(imodel, iModel):
            session.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = session.imodel
        self.form_template = template or self.default_template
        self.validator = (
            Validator(rulebook=rulebook) if rulebook else Validator()
        )

    async def pchat(self, *args, **kwargs):
        """
        Asynchronously performs a parallel chat interaction.

        Args:
            *args: Positional arguments to pass to the _parallel_chat method.
            **kwargs: Keyword arguments to pass to the _parallel_chat method,
                      including retry configurations.

        Returns:
            Any: The result of the parallel chat interaction.
        """
        kwargs = {**retry_kwargs, **kwargs}
        return await rcall(self._parallel_chat, *args, **kwargs)

    async def _parallel_chat(
        self,
        instruction: str,
        num_instances=1,
        context=None,
        sender=None,
        messages=None,
        tools=False,
        out=True,
        invoke: bool = True,
        requested_fields=None,
        persist_path=None,
        branch_config={},
        explode=False,
        include_mapping=True,
        default_key="response",
        **kwargs,
    ):
        """
        Asynchronously performs the core logic for parallel chat interactions.

        Args:
            instruction (str): The instruction to perform.
            num_instances (int, optional): Number of instances to run in parallel.
                                           Defaults to 1.
            context (Any, optional): The context to perform the instruction on.
            sender (str, optional): The sender of the instruction. Defaults to None.
            messages (list, optional): The list of messages. Defaults to None.
            tools (bool, optional): Flag indicating if tools should be used.
                                    Defaults to False.
            out (bool, optional): Flag indicating if output should be returned.
                                  Defaults to True.
            invoke (bool, optional): Flag indicating if tools should be invoked.
                                     Defaults to True.
            requested_fields (list, optional): Fields to request from the context.
                                               Defaults to None.
            persist_path (str, optional): Path to persist the branch. Defaults to None.
            branch_config (dict, optional): Configuration for the branch. Defaults to {}.
            explode (bool, optional): Flag indicating if combinations of instructions
                                      and context should be exploded. Defaults to False.
            include_mapping (bool, optional): Flag indicating if instruction, context,
                                              and branch mapping should be included.
                                              Defaults to True.
            default_key (str, optional): The default key for the response. Defaults to "response".
            **kwargs: Additional keyword arguments for further customization.

        Returns:
            Any: The result of the parallel chat interaction.
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
                requested_fields=requested_fields,
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
            tasks = [
                _inner_2(i, ins_=ins_) for ins_ in convert.to_list(instruction)
            ]
            ress = await AsyncUtil.execute_tasks(*tasks)
            return convert.to_list(ress)

        async def _inner_3_b(i):
            """different context but same instruction"""
            tasks = [
                _inner_2(i, cxt_=cxt_) for cxt_ in convert.to_list(context)
            ]
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
