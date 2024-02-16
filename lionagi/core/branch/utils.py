import pandas as pd
import json
from datetime import datetime
from typing import Union, Optional

from ...utils.sys_util import strip_lower, to_dict
from ...utils.nested_util import nget
from ...utils.df_util import to_df, search_keywords


class MessageUtil:

    @staticmethod
    def validate_messages(messages):
        if list(messages.columns) != ['node_id', 'role', 'sender', 'timestamp', 'content']:
            raise ValueError('Invalid messages dataframe. Unmatched columns.')
        if messages.isnull().values.any():
            raise ValueError('Invalid messages dataframe. Cannot have null.')
        if not all(role in ['system', 'user', 'assistant'] for role in messages['role'].unique()):
            raise ValueError('Invalid messages dataframe. Cannot have role other than ["system", "user", "assistant"].')
        for cont in messages['content']:
            if cont.startswith('Sender'):
                cont = cont.split(':', 1)[1]
            try:
                json.loads(cont)
            except:
                raise ValueError('Invalid messages dataframe. Content expect json string.')
        return True

    @staticmethod
    def sign_message(messages, sender: str):
        if sender is None or strip_lower(sender) == 'none':
            raise ValueError("sender cannot be None")
        df = to_df(messages)

        for i in df.index:
            if not df.loc[i, 'content'].startswith('Sender'):
                df.loc[i, 'content'] = f"Sender {sender}: {df.loc[i, 'content']}"
            else:
                content = df.loc[i, 'content'].split(':', 1)[1]
                df.loc[i, 'content'] = f"Sender {sender}: {content}"
                
        return to_df(df)

    @staticmethod
    def filter_messages_by(
        messages,
        role: Optional[str] = None, 
        sender: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        content_keywords: Optional[Union[str, list]] = None,
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        
        try:
            outs = messages.copy()
            
            if content_keywords:
                outs = search_keywords(content_keywords, case_sensitive)
            
            outs = outs[outs['role'] == role] if role else outs
            outs = outs[outs['sender'] == sender] if sender else outs
            outs = outs[outs['timestamp'] > start_time] if start_time else outs
            outs = outs[outs['timestamp'] < end_time] if end_time else outs
        
            return to_df(outs)
        
        except Exception as e:
            raise ValueError(f"Error in filtering messages: {e}")

    @staticmethod
    def remove_message(messages, node_id: str) -> bool:
        initial_length = len(messages)
        messages = messages[messages["node_id"] != node_id]
    
        return len(messages) < initial_length

    @staticmethod
    def get_message_rows(
        messages, 
        sender: Optional[str] = None, 
        role: Optional[str] = None, 
        n: int = 1, 
        sign_ = False, 
        from_="front",
    ) -> pd.DataFrame:

        if from_ == "last":
            if sender is None and role is None:
                outs = messages.iloc[-n:]
            elif sender and role:
                outs = messages[
                    (messages['sender'] == sender) & (messages['role'] == role)
                ].iloc[-n:]
                
            elif sender:
                outs = messages[messages['sender'] == sender].iloc[-n:]
            else:
                outs = messages[messages['role'] == role].iloc[-n:]
                
        elif from_ == "front":
            if sender is None and role is None:
                outs = messages.iloc[:n]
            elif sender and role:
                outs = messages[(messages['sender'] == sender) & (messages['role'] == role)].iloc[:n]
            elif sender:
                outs = messages[messages['sender'] == sender].iloc[:n]
            else:
                outs = messages[messages['role'] == role].iloc[:n]

        return MessageUtil.sign_message(outs, sender) if sign_ else outs

    @staticmethod
    def extend(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        MessageUtil.validate_messages(df2)
        try:
            if len(df2.dropna(how='all')) > 0 and len(df1.dropna(how='all')) > 0:
                df = to_df([df1, df2])
                df.drop_duplicates(
                    inplace=True, subset=['node_id'], keep='first', **kwargs
                )
                return to_df(df)
        except Exception as e:
            raise ValueError(f"Error in extending messages: {e}")

    @staticmethod
    def to_markdown_string(messages):
        answers = []
        for _, i in messages.iterrows():
            content = to_dict(i.content)
            
            if i.role == "assistant":
                try:
                    a = nget(content, ['action_response', 'func'])
                    b = nget(content, ['action_response', 'arguments'])
                    c = nget(content, ['action_response', 'output'])
                    if a is not None:
                        answers.append(f"Function: {a}")
                        answers.append(f"Arguments: {b}")
                        answers.append(f"Output: {c}")
                    else:
                        answers.append(nget(content, ['response']))
                except:
                    pass
            elif i.role == "user":
                try:
                    answers.append(nget(content, ['instruction']))
                except:
                    pass
            else:
                try:
                    answers.append(nget(content, ['system_info']))
                except:
                    pass
        
        out_ = "\n".join(answers)
        return out_
