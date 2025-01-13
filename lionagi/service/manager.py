# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols._concepts import Manager
from lionagi.utils import is_same_dtype

from .endpoints.chat_completion import ChatCompletionEndPoint
from .imodel import iModel


class iModelManager(Manager):

    def __init__(self, *args: iModel, **kwargs):
        super().__init__()

        self.registry: dict[str, iModel] = {}
        if args:
            if not is_same_dtype(args, iModel):
                raise TypeError("Input models are not instances of iModel")
            for model in args:
                self.register_imodel(model.endpoint.endpoint, model)

        if kwargs:
            for name, model in kwargs.items():
                self.register_imodel(name, model)

    @property
    def chat(self) -> iModel | None:
        return self.registry.get("chat", None)

    @property
    def parse(self) -> iModel | None:
        return self.registry.get("parse", None)

    def register_imodel(self, name: str, model: iModel):
        if isinstance(model.endpoint, ChatCompletionEndPoint):
            if name != "parse":
                self.registry["chat"] = model
            else:
                self.registry["parse"] = model
        elif isinstance(model, iModel):
            self.registry[name] = model
        else:
            raise TypeError("Input model is not an instance of iModel")
