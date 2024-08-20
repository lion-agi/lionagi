from typing_extensions import override
import aiohttp
from pydantic import Field

from lion_core.action.base import ObservableAction
from lion_core.action.status import ActionStatus

from lionagi.os.service.utils import call_api
from lionagi.os.service.config import RETRY_CONFIG


class APICalling(ObservableAction):

    payload: dict = Field(default_factory=dict)
    base_url: str = Field(default=None)
    endpoint: str = Field(default=None)
    api_key: str = Field(default=None, exclude=True)
    method: str = Field("post")
    required_tokens: int = Field(default=1, exclude=True)
    api_key_schema: str = Field(default=None, exclude=True)
    content_fields: list = ["response", "payload"]

    def __init__(
        self,
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        retry_config=RETRY_CONFIG,
        required_tokens=1,
        api_key_schema=None,
    ):
        super().__init__(retry_config)
        self.payload = payload
        self.base_url = base_url
        self.endpoint = endpoint
        self.api_key = api_key
        self.method = method
        self.required_tokens = required_tokens
        self.api_key_schema = api_key_schema

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
                    headers=headers,
                    json=self.payload,
                    timing=True,
                    **self.retry_config,
                )
                if response:
                    self.response = response
                    self.execution_time = elp
                    self.status = ActionStatus.COMPLETED

            except Exception as e:
                self.status = ActionStatus.FAILED
                self.error = str(e)

    @override
    def to_dict(self):
        dict_ = super().to_dict()
        dict_["api_key"] = (
            self.api_key[:6] + "*" * (len(self.api_key) - 10) + self.api_key[-4:]
        )
        dict_["status"] = self.status.value
        return dict_

    @classmethod
    def from_dict(cls, dict_):
        raise NotImplementedError

    @override
    @property
    def request(self):
        return {
            "required_tokens": self.required_tokens,
        }


# File: lionagi/os/service/api/utils.py
