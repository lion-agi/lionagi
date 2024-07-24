from typing import List, Dict, Any, Tuple, Union, Callable, Type
from lion_core import LN_UNDEFINED
from lion_core.imodel.imodel import iModel as CoreModel
from lionagi.os.service.api.endpoint import EndPoint
from lionagi.os.service.api.base_service import BaseService


class iModel(CoreModel):

    def __init__(self, service: BaseService):
        super().__init__()
        self.service = service

    async def call(
        self,
        input_: Any,
        endpoint: str | EndPoint = None,
        *,
        endpoint_config: dict | None = None,
        method: str = "post",
        retries: int | None = None,
        initial_delay: float | None = None,
        delay: float | None = None,
        backoff_factor: float | None = None,
        default: Any = LN_UNDEFINED,
        timeout: float | None = None,
        verbose: bool = True,
        error_msg: str | None = None,
        error_map: dict[type, Callable[[Exception], Any]] | None = None,
        required_tokens: int | None = None,
        cached: bool = False,
        **kwargs,
    ):
        return await self.service.serve(
            input_=input_,
            endpoint=endpoint,
            endpoint_config=endpoint_config,
            method=method,
            retries=retries,
            initial_delay=initial_delay,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            verbose=verbose,
            error_msg=error_msg,
            error_map=error_map,
            required_tokens=required_tokens,
            cached=cached,
            **kwargs,
        )

    async def chat_completion(self, messages, message_parser=None, **kwargs): ...
