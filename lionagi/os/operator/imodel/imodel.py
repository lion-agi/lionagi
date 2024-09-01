from typing import Any, Callable, Literal
from lion_core.imodel.imodel import iModel as CoreiModel
from pydantic import Field

from lionagi.os.operator import imodel
from lionagi.os.sys_utils import SysUtil
from lionagi.os.primitives import pile, Log, Node
from lionagi.os.libs import bcall, to_list, alcall

from lionagi.os.service.provider import ProviderService
from lionagi.os.service.rate_limiter import RateLimitedExecutor
from lionagi.os.service.endpoint import EndPoint
from lionagi.os.service.schema import EndpointSchema


class iModel(CoreiModel):

    service: ProviderService | None = Field(default=None, exclude=True)
    log_manager: ...

    def __init__(
        self,
        *,
        model=None,
        provider: str = None,
        api_key=None,
        api_key_schema=None,
        interval: int = None,
        interval_request: int = None,
        interval_token: int | None = None,
        endpoint: str = None,
        active_endpoint: EndPoint | None = None,
        endpoint_schema: EndpointSchema = None,
        rate_limiter: RateLimitedExecutor = None,  # priority 1
        refresh_time: float = 1,
        service: ProviderService | None = None,
        **kwargs,  # additional arguments for the model
    ):
        super().__init__()

        if not active_endpoint:
            endpoint = endpoint or "chat/completions"

        if not service:
            from lionagi.app.model_service import ModelService

            self.service = ModelService.create_service(
                provider=provider,
                api_key=api_key,
                api_key_schema=api_key_schema,
            )

        if not active_endpoint:
            self.service.add_endpoint(
                model=model,
                endpoint=endpoint,
                schema=endpoint_schema,
                interval=interval,
                interval_request=interval_request,
                interval_token=interval_token,
                refresh_time=refresh_time,
                rate_limiter=rate_limiter,
            )
        else:
            if rate_limiter:
                active_endpoint.rate_limiter = rate_limiter
            self.service.active_endpoints[active_endpoint.endpoint] = active_endpoint

        if kwargs:
            self.update_config(active_endpoint.endpoint, **kwargs)

    @property
    def provider(self):
        return self.service.config.provider

    def update_config(self, endpoint="chat/completions", **kwargs):
        self.service.active_endpoints[endpoint].update_config(**kwargs)

    async def call(
        self,
        *,
        endpoint: str,
        input_: Any,
        method: str = "post",
        retry_config=None,
        **kwargs,
    ) -> Log:
        log_ = await self.service.serve(
            endpoint=endpoint,
            input_=input_,
            method=method,
            retry_config=retry_config,
            **kwargs,
        )

    async def chat(self, messages, **kwargs) -> Log:
        return await self.service.serve_chat(messages, **kwargs)

    async def embed(self, embed_str: list[str], **kwargs) -> Log:
        return await self.call(input_=embed_str, endpoint="embeddings", **kwargs)

    async def embed_node(
        self, node: Node, field: str = "content", **kwargs
    ) -> Node: ...

    # async def structure(self, *args, **kwargs):
    #     """raise error, or return structured output"""
    #     raise NotImplementedError

    # async def compute_perplexity(
    #     self,
    #     initial_context: str = None,
    #     tokens: list[str] = None,
    #     system_msg: str = None,
    #     n_samples: int = 1,  # number of samples used for the computation per chunk
    #     use_residual: bool = True,  # whether to use residual for the last sample
    #     **kwargs,  # additional arguments for the model
    # ):
    #     from .extension import iModelExtension

    #     return await iModelExtension.compute_perplexity(
    #         imodel=self,
    #         initial_context=initial_context,
    #         tokens=tokens,
    #         system_msg=system_msg,
    #         n_samples=n_samples,
    #         use_residual=use_residual,
    #         **kwargs,
    #     )

    # async def embed_nodes(self, nodes: Any, field="content", **kwargs):
    #     from .extension import iModelExtension

    #     items = await alcall(
    #         func=iModelExtension.embed_node,
    #         input_=nodes,
    #         imodel=self,
    #         field=field,
    #         **kwargs,
    #     )

    #     return pile(items)
