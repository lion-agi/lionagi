from typing import Any
import json
from pathlib import Path
from lionagi.os import SysUtil, Converter, lionfuncs as ln


class JSONStringConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: str, **kwargs: Any) -> dict:
        return json.loads(obj, **kwargs)

    @staticmethod
    def to_obj(self, **kwargs: Any) -> str:
        return json.dumps(ln.to_dict(self), **kwargs)


class JSONFileConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: str | Path, **kwargs: Any) -> dict:
        return json.load(fp=obj, **kwargs)

    @staticmethod
    def to_obj(self, persist_path: str | Path, path_kwargs: dict = {}, **kwargs: Any):
        text = JSONStringConverter.to_obj(self, **kwargs)
        path_kwargs = SysUtil._get_path_kwargs(
            persist_path=persist_path,
            postfix="json",
            **path_kwargs,
        )
        path_ = SysUtil.create_path(**path_kwargs)
        json.dump(obj=text, fp=path_)
