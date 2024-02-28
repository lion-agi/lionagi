import json

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from lionagi.util import ConvertUtil, to_dict, to_df, nget, lcall
from lionagi.core.session.base.schema import System, Instruction, Response, BaseMessage


class MessageUtil:

    @staticmethod
    def create_message(
        system: dict[str, Any] | str | List[Any] | System | None = None,
        instruction: dict[str, Any] | str | List[Any] | Instruction | None = None,
        context: str | Dict[str, Any] | None = None,
        response: dict[str, Any] | List[Any] | str | Response | None = None,
        **kwargs
    ) -> BaseMessage:
        """
        Creates a message object based on the input parameters, ensuring only one message role is present.

        Args:
            system: Information for creating a System message.
            instruction: Information for creating an Instruction message.
            context: Context information for the message.
            response: Response data for creating a message.
            **kwargs: Additional keyword arguments for message creation.

        Returns:
            A message object of the appropriate type based on provided inputs.

        Raises:
            ValueError: If more than one of the role-specific parameters are provided.
        """
        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")

        else:
            if isinstance(system, System):
                return system
            elif isinstance(instruction, Instruction):
                return instruction
            elif isinstance(response, Response):
                return response

            msg = 0
            if response:
                msg = Response(response=response, **kwargs)
            elif instruction:
                msg = Instruction(instruction=instruction,
                                  context=context, **kwargs)
            elif system:
                msg = System(system=system, **kwargs)
            return msg

    @staticmethod
    def validate_messages(messages: pd.DataFrame) -> bool:
        """
        Validates the format and content of a DataFrame containing messages.

        Args:
            messages: A DataFrame with message information.

        Returns:
            True if the messages DataFrame is correctly formatted, False otherwise.

        Raises:
            ValueError: If the DataFrame does not match expected schema or content requirements.
        """

        if list(messages.columns) != [
            "node_id",
            "timestamp",
            "role",
            "sender",
            "content",
        ]:
            raise ValueError("Invalid messages dataframe. Unmatched columns.")
        if messages.isnull().values.any():
            raise ValueError("Invalid messages dataframe. Cannot have null.")
        if not all(
            role in ["system", "user", "assistant"]
            for role in messages["role"].unique()
        ):
            raise ValueError(
                'Invalid messages dataframe. Cannot have role other than ["system", "user", "assistant"].'
            )
        for cont in messages["content"]:
            if cont.startswith("Sender"):
                cont = cont.split(":", 1)[1]
            try:
                json.loads(cont)
            except:
                raise ValueError(
                    "Invalid messages dataframe. Content expect json string."
                )
        return True

    @staticmethod
    def sign_message(messages: pd.DataFrame, sender: str) -> pd.DataFrame:
        """
        Appends a sender prefix to the 'content' field of each message in a DataFrame.

        Args:
            messages: A DataFrame containing message data.
            sender: The identifier of the sender to prefix to message contents.

        Returns:
            A DataFrame with sender-prefixed message contents.

        Raises:
            ValueError: If the sender is None or the value is 'none'.
        """

        if sender is None or ConvertUtil.strip_lower(sender) == "none":
            raise ValueError("sender cannot be None")
        df = to_df(messages)

        for i in df.index:
            if not df.loc[i, "content"].startswith("Sender"):
                df.loc[i, "content"] = f"Sender {sender}: {df.loc[i, 'content']}"
            else:
                content = df.loc[i, "content"].split(":", 1)[1]
                df.loc[i, "content"] = f"Sender {sender}: {content}"

        return to_df(df)

    @staticmethod
    def filter_messages_by(
        messages: pd.DataFrame,
        role: str | None = None,
        sender: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        content_keywords: str | List[str] | None = None,
        case_sensitive: bool = False,
    ) -> pd.DataFrame:
        """
        Filters messages in a DataFrame based on specified criteria.

        Args:
            messages: The DataFrame to filter.
            role: The role to filter by.
            sender: The sender to filter by.
            start_time: The minimum timestamp for messages.
            end_time: The maximum timestamp for messages.
            content_keywords: Keywords to look for in message content.
            case_sensitive: Whether the keyword search should be case-sensitive.

        Returns:
            A filtered DataFrame based on the specified criteria.
        """

        try:
            outs = messages.copy()

            if content_keywords:
                outs = MessageUtil.search_keywords(outs, keywords=content_keywords, case_sensitive=case_sensitive)

            outs = outs[outs["role"] == role] if role else outs
            outs = outs[outs["sender"] == sender] if sender else outs
            outs = outs[outs["timestamp"] > start_time] if start_time else outs
            outs = outs[outs["timestamp"] < end_time] if end_time else outs

            return to_df(outs)

        except Exception as e:
            raise ValueError(f"Error in filtering messages: {e}")

    @staticmethod
    def remove_message(messages: pd.DataFrame, node_id: str) -> bool:
        """
        Removes a message from the DataFrame based on its node ID.

        Args:
            messages: The DataFrame containing messages.
            node_id: The unique identifier of the message to be removed.

        Returns:
            If any messages are removed.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> updated_messages = MessageUtil.remove_message(messages, "node_id_123")
        """

        initial_length = len(messages)
        messages.drop(messages[messages['node_id'] == node_id].index, inplace=True)
        messages.reset_index(drop=True, inplace=True)

        return len(messages) < initial_length

    @staticmethod
    def get_message_rows(
        messages: pd.DataFrame,
        sender: str | None = None,
        role: str | None = None,
        n: int = 1,
        sign_: bool = False,
        from_: str = "front",
    ) -> pd.DataFrame:
        """
        Retrieves a specified number of message rows based on sender and role.

        Args:
            messages: The DataFrame containing messages.
            sender: Filter messages by the sender.
            role: Filter messages by the role.
            n: The number of messages to retrieve.
            sign_: If True, sign the message with the sender.
            from_: Specify retrieval from the 'front' or 'last' of the DataFrame.

        Returns:
            A DataFrame containing the filtered messages.
        """

        outs = ""

        if from_ == "last":
            if sender is None and role is None:
                outs = messages.iloc[-n:]
            elif sender and role:
                outs = messages[
                    (messages["sender"] == sender) & (messages["role"] == role)
                ].iloc[-n:]

            elif sender:
                outs = messages[messages["sender"] == sender].iloc[-n:]
            else:
                outs = messages[messages["role"] == role].iloc[-n:]

        elif from_ == "front":
            if sender is None and role is None:
                outs = messages.iloc[:n]
            elif sender and role:
                outs = messages[
                    (messages["sender"] == sender) & (messages["role"] == role)
                ].iloc[:n]
            elif sender:
                outs = messages[messages["sender"] == sender].iloc[:n]
            else:
                outs = messages[messages["role"] == role].iloc[:n]

        return MessageUtil.sign_message(outs, sender) if sign_ else outs

    @staticmethod
    def extend(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Extends a DataFrame with another DataFrame's rows, ensuring no duplicate 'node_id'.

        Args:
            df1: The primary DataFrame.
            df2: The DataFrame to merge with the primary DataFrame.
            **kwargs: Additional keyword arguments for `drop_duplicates`.

        Returns:
            A DataFrame combined from df1 and df2 with duplicates removed based on 'node_id'.

        Examples:
            >>> df_main = pd.DataFrame([...])
            >>> df_additional = pd.DataFrame([...])
            >>> combined_df = MessageUtil.extend(df_main, df_additional, keep='first')
        """

        MessageUtil.validate_messages(df2)
        try:
            if len(df2.dropna(how="all")) > 0 and len(df1.dropna(how="all")) > 0:
                df = to_df([df1, df2])
                df.drop_duplicates(
                    inplace=True, subset=["node_id"], keep="first", **kwargs
                )
                return to_df(df)
        except Exception as e:
            raise ValueError(f"Error in extending messages: {e}")

    @staticmethod
    def to_markdown_string(messages: pd.DataFrame) -> str:
        """
        Converts messages in a DataFrame to a Markdown-formatted string for easy reading.

        Args:
            messages: A DataFrame containing messages with columns for 'role' and 'content'.

        Returns:
            A string formatted in Markdown, where each message's content is presented
            according to its role in a readable format.
        """

        answers = []
        for _, i in messages.iterrows():
            content = to_dict(i.content)

            if i.role == "assistant":
                try:
                    a = nget(content, ["action_response", "func"])
                    b = nget(content, ["action_response", "arguments"])
                    c = nget(content, ["action_response", "output"])
                    if a is not None:
                        answers.append(f"Function: {a}")
                        answers.append(f"Arguments: {b}")
                        answers.append(f"Output: {c}")
                    else:
                        answers.append(nget(content, ["assistant_response"]))
                except:
                    pass
            elif i.role == "user":
                try:
                    answers.append(nget(content, ["instruction"]))
                except:
                    pass
            else:
                try:
                    answers.append(nget(content, ["system_info"]))
                except:
                    pass

        out_ = "\n".join(answers)
        return out_

    @staticmethod
    def search_keywords(
        df: pd.DataFrame,
        keywords: str | List[str],
        col: str = "content",
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False,
    ) -> pd.DataFrame:
        """
        Filters a DataFrame for rows where a specified column contains given keywords.

        Args:
            df: The DataFrame to search through.
            keywords: A keyword or list of keywords to search for.
            col: The column to perform the search in. Defaults to "content".
            case_sensitive: Whether the search should be case-sensitive. Defaults to False.
            reset_index: Whether to reset the DataFrame's index after filtering. Defaults to False.
            dropna: Whether to drop rows with NA values before searching. Defaults to False.

        Returns:
            A filtered DataFrame containing only rows where the specified column contains
            any of the provided keywords.
        """

        if isinstance(keywords, list):
            keywords = "|".join(keywords)

        def handle_cases():
            if not case_sensitive:
                return df[df[col].str.contains(keywords, case=False)]
            else:
                return df[df[col].str.contains(keywords)]

        out = handle_cases()
        if reset_index or dropna:
            out = to_df(out, reset_index=reset_index)

        return out

    @staticmethod
    def replace_keyword(
        df: pd.DataFrame,
        keyword: str,
        replacement: str,
        col: str = "content",
        case_sensitive: bool = False,
    ) -> None:
        """
        Replaces occurrences of a specified keyword with a replacement string in a DataFrame column.

        Args:
            df: The DataFrame to modify.
            keyword: The keyword to be replaced.
            replacement: The string to replace the keyword with.
            col: The column in which to perform the replacement.
            case_sensitive: If True, performs a case-sensitive replacement. Defaults to False.
        """

        if not case_sensitive:
            df.loc[:, col] = df[col].str.replace(keyword, replacement, case=False, regex=False)
        else:
            df.loc[:, col] = df[col].str.replace(keyword, replacement, regex=False)

    @staticmethod
    def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
        """
        Reads a CSV file into a DataFrame with optional additional pandas read_csv parameters.

        Args:
            filepath: The path to the CSV file to read.
            **kwargs: Additional keyword arguments to pass to pandas.read_csv function.

        Returns:
            A DataFrame containing the data read from the CSV file.
        """
        df = pd.read_csv(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def read_json(filepath, **kwargs):
        df = pd.read_json(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def remove_last_n_rows(df: pd.DataFrame, steps: int) -> pd.DataFrame:
        """
        Removes the last 'n' rows from a DataFrame.

        Args:
            df: The DataFrame from which to remove rows.
            steps: The number of rows to remove from the end of the DataFrame.

        Returns:
            A DataFrame with the last 'n' rows removed.

        Raises:
            ValueError: If 'steps' is negative or greater than the number of rows in the DataFrame.
        """

        if steps < 0 or steps > len(df):
            raise ValueError(
                "'steps' must be a non-negative integer less than or equal to "
                "the length of DataFrame."
            )
        return to_df(df[:-steps])

    @staticmethod
    def update_row(df: pd.DataFrame, row: str | int, col: str | int, value: Any) -> bool:
        """
        Updates a row's value for a specified column in a DataFrame.

        Args:
            df: The DataFrame to update.
            col: The column whose value is to be updated.
            old_value: The current value to search for in the specified column.
            new_value: The new value to replace the old value with.

        Returns:
            True if the update was successful, False otherwise.
        """

        # index = df.index[df[col] == old_value].tolist()
        # if index:
        #     df.at[index[0], col] = new_value
        #     return True
        # return False
        try:
            df.loc[row, col] = value
            return True
        except:
            return False

    # @staticmethod
    # def to_json_content(value):
    #     if isinstance(value, dict):
    #         for key, val in value.items():
    #             value[key] = MessageUtil.to_json_content(val)
    #         value = json.dumps(value)
    #     if isinstance(value, list):
    #         for i in range(len(value)):
    #             value[i] = MessageUtil.to_json_content(value[i])
    #     return value

    # @staticmethod
    # def to_dict_content(value):
    #     try:
    #         value = json.loads(value)
    #         if isinstance(value, dict):
    #             for key, val in value.items():
    #                 value[key] = MessageUtil.to_dict_content(val)
    #         if isinstance(value, list):
    #             for i in range(len(value)):
    #                 value[i] = MessageUtil.to_dict_content(value[i])
    #         return value
    #     except:
    #         return value

    # @staticmethod
    # def response_to_message(response: dict[str, Any], **kwargs) -> Any:
    #     """
    #     Processes a message response dictionary to generate an appropriate message object.

    #     Args:
    #         response: A dictionary potentially containing message information.
    #         **kwargs: Additional keyword arguments to pass to the message constructors.

    #     Returns:
    #         An instance of a message class, such as ActionRequest or AssistantResponse,
    #         depending on the content of the response.
    #     """
    #     try:
    #         response = response["message"]
    #         if ConvertUtil.strip_lower(response['content']) == "none":

    #             content = ActionRequest._handle_action_request(response)
    #             return ActionRequest(action_request=content, **kwargs)

    #         else:

    #             try:
    #                 if 'tool_uses' in to_dict(response[MessageField.CONTENT.value]):
    #                     content_ = to_dict(response[MessageField.CONTENT.value])[
    #                         'tool_uses']
    #                     return ActionRequest(action_request=content_, **kwargs)

    #                 elif MessageContentKey.RESPONSE.value in to_dict(
    #                         response[MessageField.CONTENT.value]):
    #                     content_ = to_dict(response[MessageField.CONTENT.value])[
    #                         MessageContentKey.RESPONSE.value]
    #                     return AssistantResponse(assistant_response=content_, **kwargs)

    #                 elif MessageContentKey.ACTION_REQUEST.value in to_dict(
    #                         response[MessageField.CONTENT.value]):
    #                     content_ = to_dict(response[MessageField.CONTENT.value])[
    #                         MessageContentKey.ACTION_REQUEST.value]
    #                     return ActionRequest(action_request=content_, **kwargs)

    #                 else:
    #                     return AssistantResponse(assistant_response=response, **kwargs)

    #             except:
    #                 return AssistantResponse(assistant_response=response, **kwargs)
    #     except:
    #         return ActionResponse(action_response=response, **kwargs)
