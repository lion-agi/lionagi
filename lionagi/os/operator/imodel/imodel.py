from typing import Any, Callable

from lion_core import LN_UNDEFINED

from lion_core.abc import BaseiModel, Observable, Temporal


from lionagi.os.sys_util import SysUtil
from lionagi.os.service.api.endpoint import EndPoint
from lionagi.os.service.api.base_service import BaseService

from .extension import iModelExtension


class iModel(BaseiModel, Observable, Temporal):

    def __init__(self, service: BaseService):
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time(type_="timestamp")
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

    async def chat(self, messages, **kwargs):
        return await self.call(messages, endpoint="chat/completions", **kwargs)

    async def embed(self, input, **kwargs):
        return await self.call(input, endpoint="embeddings", **kwargs)

    async def compute_perplexity(
        self,
        initial_context: str = None,
        tokens: list[str] = None,
        system_msg: str = None,
        n_samples: int = 1,  # number of samples used for the computation per chunk
        use_residual: bool = True,  # whether to use residual for the last sample
        **kwargs,  # additional arguments for the model
    ):
        return await iModelExtension.compute_perplexity(
            self,
            initial_context=initial_context,
            tokens=tokens,
            system_msg=system_msg,
            n_samples=n_samples,
            use_residual=use_residual,
            **kwargs,
        )

    async def embed_nodes(imodel, nodes, field, **kwargs):
        return pile
