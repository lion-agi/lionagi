from typing import Union, Dict, Any

from ..utils.sys_util import install_import
from ..utils.call_util import CallDecorator as cd
from .base_service import BaseService

class TransformersService(BaseService):
    def __init__(self, task: str = None, model: Union[str, Any] = None, config: Union[str, Dict, Any] = None, **kwargs):
        try:
            from transformers import pipeline
        except ImportError:
            try:
                install_import(
                    package_name='transformers',
                    import_name='pipeline'
                )
                from transformers import pipeline
            except Exception as e:
                raise ImportError(f'Unable to import required module from transformers. Please make sure that transformers is installed. Error: {e}')
                
        super().__init__()
        self.task = task
        self.model = model
        self.config = config
        self.pipe = pipeline(task=task, model=model, config=config, **kwargs)

    @cd.force_async
    def serve_chat(self, messages, **kwargs):
        try:
            from transformers import Conversation
        except ImportError:
            try:
                install_import(
                    package_name='transformers',
                    import_name='Conversation'
                )
                from transformers import Conversation
            except Exception as e:
                raise ImportError(f'Unable to import required module from transformers. Please make sure that transformers is installed. Error: {e}')

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
