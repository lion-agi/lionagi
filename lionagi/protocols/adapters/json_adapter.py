# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from pathlib import Path

from lionagi.protocols.adapters.adapter import Adapter, T


class JsonAdapter(Adapter):

    obj_key = "json"

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: str, /) -> dict:
        return json.loads(obj)

    @classmethod
    def to_obj(cls, subj: T) -> str:
        return json.dumps(subj.to_dict())


class JsonFileAdapter(Adapter):

    obj_key = ".json"

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: str | Path, /) -> dict:
        with open(obj) as f:
            return json.load(f)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        fp: str | Path,
    ) -> None:
        with open(fp, "w") as f:
            json.dump(subj.to_dict(), f)
        logging.info(f"Successfully saved data to {fp}")
