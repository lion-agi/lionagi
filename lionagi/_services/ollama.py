import ollama

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


class OllamaService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()
        self.model = model
        self.client = ollama.Client(**kwargs)

    @force_async
    def serve_chat(self, messages, **kwargs):
        ollama.pull(self.model)
        payload = {'messages': messages}

        try:
            completion = self.client.chat(model=self.model, messages=messages, **kwargs)
            completion['choices'] = [{'message': completion.pop('message')}]
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e