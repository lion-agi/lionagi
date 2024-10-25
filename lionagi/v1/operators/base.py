from typing import Any, Literal

from lion_core.action import func_to_tool
from lion_core.communication import System
from lion_core.log_manager import LogManager
from lion_core.session.branch import Branch
from lion_core.session.session import Session
from lion_core.setting import TimedFuncCallConfig
from lion_service import iModel
from lionabc.exceptions import ItemNotFoundError
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from lionagi.v1.llm_config import DEFAULT_CHAT_CONFIG


class Operator:

    def __init__(
        self,
        *,
        name: str | None = None,
        imodel: iModel = None,
        operative_model: type[BaseModel] = None,
        tools: Any = None,
        user: str | None = None,
        system: System | None = None,
        system_sender: str | None = None,
        system_datetime: bool | str | None = None,
        persist_dir=None,
    ):
        imodel = imodel or iModel(**DEFAULT_CHAT_CONFIG)
        session = Session(imodel=imodel, user=user, name=name)
        if system and not isinstance(system, System):
            system = System(
                system=system,
                sender=system_sender,
                system_datetime=system_datetime,
                recipient=session,
            )
            session.system = system

        elif isinstance(system, System):
            system = system.clone()
            system.sender = system_sender or "system"
            system.recipient = session.ln_id

        if operative_model:
            if isinstance(operative_model, type):
                if not issubclass(operative_model, BaseModel):
                    raise ValueError(
                        "operative_model must be a subclass of BaseModel"
                    )
            elif isinstance(operative_model, BaseModel):
                operative_model = type(operative_model)

        if tools:
            tools = func_to_tool(tools)

        self.session = session
        self.operative_model = operative_model
        self.tools = tools or []

        self.log_manager = LogManager(
            persist_dir=persist_dir or "./data/logs",
            subfolder="messages",
            file_prefix="message_",
        )

    async def lookup_branch(
        self,
        branch: Branch = None,
        name: str = None,
        new_branch: bool = False,
        **kwargs,
    ) -> str:
        """kwargs for new branch"""
        if isinstance(branch, Branch):
            return branch.ln_id
        if name:
            for i in self.session.branches:
                if i.name == name:
                    return i.ln_id
        if new_branch:
            return await self.new_branch(name=name, **kwargs)
        return self.session.default_branch.ln_id

    async def new_branch(
        self,
        *,
        system: Any = None,
        system_datetime: Any = None,
        operative_model: type[BaseModel] = None,
        user: str | None = None,
        messages: list = None,
        name: str | None = None,
        imodel: iModel = None,
        tools: Any = None,
    ) -> Branch:
        branch = await self.session.new_branch(
            operative_model=operative_model,
            system=system,
            system_sender=self.session,
            system_datetime=system_datetime,
            name=name,
            user=user,
            imodel=imodel,
            messages=messages,
            tools=tools,
        )
        return branch.ln_id

    async def operate(
        self,
        *,
        branch: Branch = None,  # priority 1
        instruction=None,
        guidance=None,
        context=None,
        progress: list[str] = None,
        conversation: str = None,
        imodel: iModel = None,
        reason: bool = True,
        actions: bool = True,
        tools: Any = None,
        images: list = None,
        num_parse_retries: int = 0,
        retry_imodel: iModel = None,
        retry_kwargs: dict = {},
        clear_messages: bool = False,
        skip_validation: bool = False,
        invoke_action: bool = True,
        system: Any = None,
        system_datetime: Any = None,
        operative_model: type[BaseModel] = None,
        user: str | None = None,
        messages: list = None,  # only apply to new branch
        new_branch: bool = False,  # priority 3
        name: str | None = None,  # priority 2
        sender=None,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        config_dict: ConfigDict | None = None,
        doc: str | None = None,
        validators: dict = None,
        use_base_kwargs: bool = False,
        inherit_base: bool = True,
        field_descriptions: dict[str, str] | None = None,
        frozen: bool = False,
        extra_fields: dict[str, FieldInfo] | None = None,
        use_all_fields: bool = False,
        image_detail: Literal["low", "high", "auto"] = None,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "force",
        action_timed_config: dict | TimedFuncCallConfig | None = None,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        **kwargs,
    ) -> BaseModel | dict | str:
        """
        additional kwargs for payload
        """
        imodel = imodel or self.session.imodel

        if actions and invoke_action and (tools is None or tools == True):
            tools = self.tools

        branch: str = await self.lookup_branch(
            branch=branch,
            name=name,
            new_branch=new_branch,
            system=system,
            system_datetime=system_datetime,
            operative_model=operative_model,
            user=user,
            messages=messages,
            imodel=imodel,
            tools=tools,
        )
        branch: Branch = self.session.branches[branch]

        len1 = len(branch.messages)

        if conversation:
            if conversation in self.session.conversations:
                progress = self.session.conversations[conversation]
            else:
                raise ItemNotFoundError(
                    f"Conversation {conversation} not found"
                )

        kwargs["progress"] = progress
        kwargs["sender"] = sender or self.session.ln_id
        kwargs["recipient"] = branch.ln_id

        out = await branch.operate(
            instruction=instruction,
            guidance=guidance,
            context=context,
            operative_model=operative_model,
            imodel=imodel,
            reason=reason,
            actions=actions,
            tools=tools,
            images=images,
            num_parse_retries=num_parse_retries,
            retry_imodel=retry_imodel,
            retry_kwargs=retry_kwargs,
            clear_messages=clear_messages,
            skip_validation=skip_validation,
            invoke_action=invoke_action,
            user=user,
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            config_dict=config_dict,
            doc=doc,
            validators=validators,
            use_base_kwargs=use_base_kwargs,
            inherit_base=inherit_base,
            field_descriptions=field_descriptions,
            frozen=frozen,
            extra_fields=extra_fields,
            use_all_fields=use_all_fields,
            image_detail=image_detail,
            handle_unmatched=handle_unmatched,
            action_timed_config=action_timed_config,
            handle_validation=handle_validation,
            **kwargs,
        )

        len2 = len(branch.messages)
        if len2 > len1:
            logs = [i.to_log() for i in branch.messages[len1:]]
            await self.log_manager.alog(logs)

        return out

    async def communicate(
        self,
        *,
        branch: Branch = None,
        instruction: Any = None,
        guidance: str | dict | list = None,
        context: str | dict | list = None,
        imodel: iModel = None,
        tools: Any = None,
        conversation=None,
        request_model: type[BaseModel] = None,
        request_fields: dict = None,
        images: list = None,
        num_parse_retries: int = 0,
        retry_imodel: iModel = None,
        retry_kwargs: dict = {},
        clear_messages: bool = False,
        invoke_action: bool = False,
        system: Any = None,
        system_datetime: Any = None,
        user: str | None = None,
        messages: list = None,
        name: str | None = None,
        new_branch: bool = False,
        **kwargs,
    ):
        imodel = imodel or self.session.imodel

        if invoke_action and (tools is None or tools == True):
            tools = self.tools

        if not branch:
            branch = await self.lookup_branch(
                name=name,
                new_branch=new_branch,
                system=system,
                system_datetime=system_datetime,
                user=user,
                messages=messages,
                imodel=imodel,
                tools=tools,
            )
            branch = self.session.branches[branch]

        len1 = len(branch.messages)
        out = await branch.communicate(
            instruction=instruction,
            guidance=guidance,
            context=context,
            progress=conversation,
            sender=self.session.ln_id,
            recipient=branch.ln_id,
            request_model=request_model,
            request_fields=request_fields,
            imodel=imodel,
            tools=tools,
            images=images,
            num_parse_retries=num_parse_retries,
            retry_imodel=retry_imodel,
            retry_kwargs=retry_kwargs,
            clear_messages=clear_messages,
            invoke_action=invoke_action,
            user=user,
            **kwargs,
        )
        len2 = len(branch.messages)
        if len2 > len1:
            logs = [i.to_log() for i in branch.messages[len1:]]
            await self.log_manager.alog(logs)

        return out
