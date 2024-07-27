import aiohttp
from pydantic import Field, field_validator

from lion_core.abc import Action
from lion_core.generic.component import Component
from lion_core.generic.note import Note
from lion_core.exceptions import (
    LionValueError,
    LionResourceError,
    LionOperationError,
)
from lion_core.libs import to_dict
from lion_core.action.status import ActionStatus


class APICalling(Component, Action):

    name: str | None = Field("API Calling")
    content: Note = Field(default_factory=Note)
    status: ActionStatus = Field(ActionStatus.PENDING)

    def __init__(
        self,
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        content=None,
        required_tokens=15,
    ):
        if not content:
            content = Note()

        super().__init__(content=content)

        content_ = {
            "method": method,
            "payload": payload,
            "base_url": base_url,
            "endpoint": endpoint,
            "required_tokens": required_tokens,
        }

        for k, v in content_.items():
            if self.content.get(k, None) is None:
                self.content.set([k], v)

        if api_key is not None:
            self.content.set(["headers"], {"Authorization": f"Bearer {api_key}"})

    @field_validator("status", mode="before")
    def _validate_status(cls, value):
        if isinstance(value, ActionStatus):
            return value
        try:
            return ActionStatus(value)
        except:
            raise LionValueError(
                f"Invalid value: status must be one of {ActionStatus.__members__.keys()}"
            )

    async def invoke(self):
        with aiohttp.ClientSession() as session:
            try:
                method = self.content.get(["method"])
                if (_m := getattr(session, method, None)) is not None:

                    async with _m(
                        url=self.content.get(["base_url"])
                        + self.content.get(["endpoint"]),
                        headers=self.content.get(["headers"]),
                        json=self.content.get(["payload"]),
                    ) as response:

                        self.status = ActionStatus.PROCESSING
                        response_json = await response.json()
                        self.content.set(["response"], response_json)
                        self.content.pop(["headers"])

                        if "error" not in response_json:
                            return

                        if "error" in response_json:
                            self.status = ActionStatus.FAILED
                            self.content.set(["error"], response_json["error"])
                            raise LionOperationError(
                                "API call failed with error: ", response_json["error"]
                            )

                        if "Rate limit" in response_json["error"].get("message", ""):
                            self.status = ActionStatus.FAILED
                            self.content.set(["error"], response_json["error"])
                            raise LionResourceError(
                                f"Rate limit exceeded. Error: {response_json['error']}"
                            )
                else:
                    self.content.pop(["headers"])
                    self.status = ActionStatus.FAILED
                    self.content.set(["error"], f"Invalid HTTP method: {method}")
                    raise LionValueError(f"Invalid HTTP method: {method}")

            except aiohttp.ClientError as e:
                self.status = ActionStatus.FAILED
                self.content.pop(["headers"])
                self.content.set(["error"], f"API call failed: {e}")
                raise LionOperationError(f"API call failed: {e}")

    def to_dict(self):
        dict_ = super().to_dict()
        dict_["content"] = self.content.to_dict()
        if "headers" in dict_["content"]:
            dict_["content"].pop("headers")
        return dict_

    @classmethod
    def from_dict(cls, dict_: dict):
        dict_["content"] = Note(**to_dict(dict_.get("content", {})))
        return cls.from_dict(dict_)
