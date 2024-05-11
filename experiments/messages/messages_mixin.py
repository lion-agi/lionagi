from abc import ABC
from functools import singledispatchmethod
from typing import Any
from pydantic import field_validator
import pandas as pd
from lionagi.libs import convert, dataframe
from lionagi.core.messages import BaseMessage, System, Instruction, Response
from lionagi.core.branch.util import MessageUtil


class BranchMessagesMixin(ABC):

    @property
    def conversation(self):
        return list(self.messages.node_id)

    @field_validator("messages")
    def _validate_messages(self, messages):
        if not MessageUtil.validate_messages(messages):
            raise ValueError("Invalid messages format")

    @field_validator("system")
    def _validate_messages(self, system: dict | str | System | None):
        if system:
            self.add_message(system=system)

    @singledispatchmethod
    def process_message_node(self, msg: Any, **kwargs):
        raise ValueError(f"{type(msg)} is an invalid message type")

    @process_message_node.register
    def process_message_node(self, msg: System, **kwargs):
        self.system_node = msg

    @process_message_node.register
    def _(self, msg: Instruction, **kwargs):
        recipient = kwargs.get("recipient", None)

        msg.recipient = recipient or self.name or self.id_

    @process_message_node
    def _(self, msg: Response, **kwargs):
        recipient = kwargs.get("recipient", None)

        if "action_response" in msg.content:
            msg.recipient = recipient or self.name or self.id_

        elif "response" in msg.content:
            msg.sender = self.name or self.id_

    def add_message(
        self,
        system: dict | list | System | None = None,
        instruction: dict | list | Instruction | None = None,
        context: str | dict[str, Any] | None = None,
        response: dict | list | BaseMessage | None = None,
        output_fields: dict | None = None,
        recipient: str | None = None,
        **kwargs,
    ) -> None:

        _msg = MessageUtil.create_message(
            system=system,
            instruction=instruction,
            context=context,
            response=response,
            output_fields=output_fields,
            recipient=recipient,
            **kwargs,
        )

        self.process_message_node(_msg, recipient=recipient)
        if _msg.id_ not in self.message_log:
            self.message_log[_msg.id_] = _msg

        self.append_to_conversation(_msg)

    def append_to_conversation(self, msg: BaseMessage):
        _msg: BaseMessage = msg.copy()
        _msg.content = msg.msg_content

        self.messages.loc[len(self.messages)] = _msg.to_pd_series()

    def _to_chatcompletion_message(
        self, with_sender: bool = False
    ) -> list[dict[str, Any]]:

        return [
            self.message_log[i].signed_msg if with_sender else self.message_log[i].msg
            for i in self.conversation
        ]

    @property
    def chat_messages(self) -> list[dict[str, Any]]:
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self) -> list[dict[str, Any]]:
        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> pd.DataFrame:
        return MessageUtil.get_message_rows(self.messages, n=1, from_="last")

    @property
    def last_message_content(self) -> dict[str, Any]:
        return convert.to_dict(self.messages.content.iloc[-1])

    @property
    def last_response(self) -> pd.DataFrame:
        """
        Retrieves the last message marked with the 'assistant' role.

        Returns:
                A pandas Series representing the last 'assistant' (response) message in the branch.
        """

        return MessageUtil.get_message_rows(
            self.messages, role="assistant", n=1, from_="last"
        )

    @property
    def last_response_content(self) -> dict[str, Any]:
        """
        Extracts the content of the last 'assistant' (response) message.

        Returns:
                A dictionary representing the content of the last 'assistant' message.
        """

        return convert.to_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> pd.DataFrame:
        """
        Filters and retrieves all messages sent by 'action_request'.

        Returns:
                A pandas DataFrame containing all 'action_request' messages.
        """

        return convert.to_df(self.messages[self.messages.sender == "action_request"])

    @property
    def action_response(self) -> pd.DataFrame:
        """
        Filters and retrieves all messages sent by 'action_response'.

        Returns:
                A pandas DataFrame containing all 'action_response' messages.
        """

        return convert.to_df(self.messages[self.messages.sender == "action_response"])

    @property
    def responses(self) -> pd.DataFrame:
        """
        Retrieves all messages marked with the 'assistant' role.

        Returns:
                A pandas DataFrame containing all messages with an 'assistant' role.
        """

        return convert.to_df(self.messages[self.messages.role == "assistant"])

    @property
    def assistant_responses(self) -> pd.DataFrame:
        """
        Filters 'assistant' role messages excluding 'action_request' and 'action_response'.

        Returns:
                A pandas DataFrame of 'assistant' messages excluding action requests/responses.
        """

        a_responses = self.responses[self.responses.sender != "action_response"]
        a_responses = a_responses[a_responses.sender != "action_request"]
        return convert.to_df(a_responses)

    @property
    def last_assistant_response(self):
        return self.assistant_responses.iloc[-1]

    @property
    def info(self) -> dict[str, Any]:
        """
        Summarizes branch information, including message counts by role.

        Returns:
                A dictionary containing counts of messages categorized by their role.
        """

        return self._info()

    @property
    def sender_info(self) -> dict[str, int]:
        """
        Provides a summary of message counts categorized by sender.

        Returns:
                A dictionary with senders as keys and counts of their messages as values.
        """

        return self._info(use_sender=True)

    @property
    def describe(self) -> dict[str, Any]:
        """
        Provides a detailed description of the branch, including a summary of messages.

        Returns:
                A dictionary with a summary of total messages, a breakdown by role, and
                a preview of the first five messages.
        """

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [msg.to_dict() for _, msg in self.messages.iterrows()][
                : len(self.messages) - 1 if len(self.messages) < 5 else 5
            ],
        }

    def search_keywords(
        self,
        keywords: str | list[str],
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False,
    ) -> pd.DataFrame:
        return dataframe.search_keywords(
            self.messages,
            keywords,
            case_sensitive=case_sensitive,
            reset_index=reset_index,
            dropna=dropna,
        )

    def extend(self, messages: pd.DataFrame, **kwargs) -> None:

        self.messages = MessageUtil.extend(self.messages, messages, **kwargs)

    def filter_by(
        self,
        role: str | None = None,
        sender: str | None = None,
        start_time=None,
        end_time=None,
        content_keywords: str | list[str] | None = None,
        case_sensitive: bool = False,
    ) -> pd.DataFrame:

        return MessageUtil.filter_messages_by(
            self.messages,
            role=role,
            sender=sender,
            start_time=start_time,
            end_time=end_time,
            content_keywords=content_keywords,
            case_sensitive=case_sensitive,
        )

    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the branch based on its node ID.

        Args:
                node_id: The unique identifier of the message to be removed.
        """
        MessageUtil.remove_message(self.messages, node_id)

    def update_message(self, node_id: str, column: str, value: Any) -> bool:
        """
        Updates a specific column of a message identified by node_id with a new value.

        Args:
                value: The new value to update the message with.
                node_id: The unique identifier of the message to update.
                column: The column of the message to update.
        """

        index = self.messages[self.messages["node_id"] == node_id].index[0]

        return dataframe.update_row(
            self.messages, row=index, column=column, value=value
        )

    def change_first_system_message(
        self, system: str | dict[str, Any] | System, sender: str | None = None
    ) -> None:
        """
        Updates the first system message with new content and/or sender.

        Args:
                system: The new system message content or a System object.
                sender: The identifier of the sender for the system message.
        """

        if len(self.messages[self.messages["role"] == "system"]) == 0:
            raise ValueError("There is no system message in the messages.")

        if not isinstance(system, (str, dict, System)):
            raise ValueError("Input cannot be converted into a system message.")

        if isinstance(system, (str, dict)):
            system = System(system, sender=sender)

        if isinstance(system, System):
            from lionagi.libs import SysUtil

            system.timestamp = SysUtil.get_timestamp()
            sys_index = self.messages[self.messages.role == "system"].index
            self.messages.loc[sys_index[0]] = system.to_pd_series()

    def rollback(self, steps: int) -> None:
        """
        Removes the last 'n' messages from the branch.

        Args:
                steps: The number of messages to remove from the end.
        """

        self.messages = dataframe.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the branch.
        """
        self.messages = dataframe.ln_DataFrame(columns=self._columns)

    def replace_keyword(
        self,
        keyword: str,
        replacement: str,
        column: str = "content",
        case_sensitive: bool = False,
    ) -> None:

        dataframe.replace_keyword(
            self.messages,
            keyword,
            replacement,
            column=column,
            case_sensitive=case_sensitive,
        )

    def messages_describe(self) -> dict[str, Any]:
        """
        Describes the messages in the branch.

        Returns:
            dict[str, Any]: A dictionary describing the messages in the branch.
        """
        return dict(
            total_messages=len(self.messages),
            summary_by_role=self._info(),
            summary_by_sender=self._info(use_sender=True),
            # instruction_sets=self.instruction_sets,
            registered_tools=self.tool_manager.registry,
            messages=[msg.to_dict() for _, msg in self.messages.iterrows()],
        )

    def _info(self, use_sender: bool = False) -> dict[str, int]:
        """
        Helper method to generate summaries of messages either by role or sender.

        Args:
                use_sender: If True, summary is categorized by sender. Otherwise, by role.

        Returns:
                A dictionary summarizing the count of messages either by role or sender.
        """

        messages = self.messages["sender"] if use_sender else self.messages["role"]
        result = messages.value_counts().to_dict()
        result["total"] = len(self.messages)
        return result
