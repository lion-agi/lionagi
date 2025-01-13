import json
import logging
from pathlib import Path

from lionagi.protocols._concepts import Collective

from .adapter import Adapter, T


class JsonAdapter(Adapter):

    obj_key = "json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str,
        /,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        """
        kwargs for json.loads(s, **kwargs)
        """
        result = json.loads(obj, **kwargs)
        if many:
            return result if isinstance(result, list) else [result]
        return (
            result[0]
            if isinstance(result, list) and len(result) > 0
            else result
        )

    @classmethod
    def to_obj(
        cls,
        subj: T,
        *,
        many: bool = False,
        **kwargs,
    ):
        """
        kwargs for json.dumps(obj, **kwargs)
        """
        if many:
            if isinstance(subj, Collective):
                return json.dumps([i.to_dict() for i in subj], **kwargs)
            return json.dumps([subj.to_dict()], **kwargs)
        return json.dumps(subj.to_dict(), **kwargs)


class JsonFileAdapter(Adapter):

    obj_key = ".json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | Path,
        /,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        """
        kwargs for json.load(fp, **kwargs)
        """
        with open(obj) as f:
            result = json.load(f, **kwargs)
        if many:
            return result if isinstance(result, list) else [result]
        return (
            result[0]
            if isinstance(result, list) and len(result) > 0
            else result
        )

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        fp: str | Path,
        many: bool = False,
        **kwargs,
    ):
        """
        kwargs for json.dump(obj, fp, **kwargs)
        """
        if many:
            if isinstance(subj, Collective):
                json.dump([i.to_dict() for i in subj], fp=fp, **kwargs)
                return
            json.dump([subj.to_dict()], fp=fp, **kwargs)
            return
        json.dump(subj.to_dict(), fp=fp, **kwargs)
        logging.info(f"Successfully saved data to {fp}")
