import aiohttp
from typing_extensions import override
from lion_core.abc import EventStatus
from lion_core.action.base import ObservableAction
from lion_core.setting import RetryConfig
from .utils import call_api

from pydantic import Field, PrivateAttr


class APICalling(ObservableAction):

    payload: dict = Field(default_factory=dict)
    base_url: str = Field(default=None)
    endpoint: str = Field(default=None)
    api_key: str | None = Field(default=None, exclude=True)
    method: str = Field("post")
    api_key_schema: str | None = Field(default=None, exclude=True)
    content_fields: list = ["execution_response", "payload"]
    _rate_limited: bool | None = PrivateAttr(False)
    _required_tokens: int | None = PrivateAttr(None)

    def __init__(
        self,
        payload: dict,
        base_url: str,
        endpoint: str,
        api_key: str,
        method: str,
        retry_config: RetryConfig,
        required_tokens: int = None,
        api_key_schema: str = None,
        rate_limited: bool = None,
    ):
        super().__init__(retry_config)
        self.payload = payload
        self.base_url = base_url
        self.endpoint = endpoint
        self.api_key = api_key
        self.method = method
        if rate_limited:
            self._rate_limited = True
            self._required_tokens = required_tokens
        self.api_key_schema = api_key_schema
        self.retry_config = self.retry_config.update(
            new_schema_obj=True,
            retry_timing=True,
        )

    @override
    async def invoke(self):
        async with aiohttp.ClientSession() as session:
            url = self.base_url + self.endpoint
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response, elp = await call_api(
                    http_session=session,
                    url=url,
                    method=self.method,
                    retry_config=self.retry_config,
                    headers=headers,
                    json=self.payload,
                )
                if response:
                    self.execution_response = response
                    self.execution_time = elp
                    self.status = EventStatus.COMPLETED

            except Exception as e:
                self.status = EventStatus.FAILED
                self.execution_error = str(e)

    @override
    def to_dict(self):
        dict_ = super().to_dict()
        dict_["api_key"] = (
            self.api_key[:6] + "*" * (len(self.api_key) - 10) + self.api_key[-4:]
        )
        dict_["status"] = self.status.value
        return dict_

    def _request(self) -> dict:
        """override this method in child class."""
        if self._required_tokens:
            return {"required_tokens": self._required_tokens}
        return {}


# File: lionagi/os/service/api/utils.py
