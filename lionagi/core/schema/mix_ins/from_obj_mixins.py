from abc import ABC
from functools import singledispatchmethod
from typing import Any, TypeVar, Type

import pandas as pd
from pydantic import BaseModel, ValidationError

import lionagi.libs.ln_convert as convert
from lionagi.libs.ln_parse import ParseUtil

T = TypeVar("T")  # Generic type for return type of from_obj method


class BaseFromObjectMixin(ABC, BaseModel):

    @singledispatchmethod
    @classmethod
    def from_obj(cls: Type[T], obj: Any, *args, **kwargs) -> T:
        raise NotImplementedError(f"Unsupported type: {type(obj)}")

    @from_obj.register(dict)
    @classmethod
    def _from_dict(cls, obj: dict, *args, **kwargs) -> T:
        return cls.model_validate(obj, *args, **kwargs)

    @from_obj.register(str)
    @classmethod
    def _from_str(cls, obj: str, *args, fuzzy_parse=False, **kwargs) -> T:
        if fuzzy_parse:
            obj = ParseUtil.fuzzy_parse_json(obj)
        else:
            obj = convert.to_dict(obj)

        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}")

    @from_obj.register(list)
    @classmethod
    def _from_list(cls, obj: list[Any], *args, **kwargs) -> list[T]:
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    @from_obj.register(pd.Series)
    @classmethod
    def _from_pd_series(cls, obj: pd.Series, *args, pd_kwargs={}, **kwargs) -> T:
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

    @from_obj.register(pd.DataFrame)
    @classmethod
    def _from_pd_dataframe(
        cls, obj: pd.DataFrame, *args, pd_kwargs={}, **kwargs
    ) -> list[T]:
        return [
            cls.from_obj(row, *args, **pd_kwargs, **kwargs) for _, row in obj.iterrows()
        ]

    @from_obj.register(BaseModel)
    @classmethod
    def _from_base_model(
        cls, obj: BaseModel, pydantic_kwargs={"by_alias": True}, **kwargs
    ) -> T:
        config_ = {**obj.model_dump(**pydantic_kwargs), **kwargs}
        return cls.from_obj(**config_)
