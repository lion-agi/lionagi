from typing import Union, Dict, Any
from transformers import pipeline, Conversation

from .base_service import BaseService

import functools
from concurrent.futures import ThreadPoolExecutor
import asyncio


def force_async(fn):
    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper


class TransformersService(BaseService):
    def __init__(self, task: str = None, model: Union[str, Any] = None, config: Union[str, Dict, Any] = None, **kwargs):
        super().__init__()
        self.task = task
        self.model = model
        self.config = config
        self.pipe = pipeline(task=task, model=model, config=config, **kwargs)

    @force_async
    def serve_chat(self, messages, **kwargs):
        if self.task:
            if self.task != 'conversational':
                raise ValueError(f"Invalid transformers pipeline task: {self.task}. Valid task: 'conversational'")

        payload = {'messages': messages}
        conversation = self.pipe(Conversation(messages), **kwargs)
        completion = {"Conversation id": conversation.uuid,
                      "model": self.pipe.model,
                      "choices": [{
                          "message": conversation.messages[-1]
                      }]
        }

        return payload, completion

