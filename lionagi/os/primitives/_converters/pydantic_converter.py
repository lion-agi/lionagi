from typing import Any
from pydantic import BaseModel, create_model
from lionagi.os import Converter, lionfuncs as ln
from lionagi.os.primitives.core_types import Component


class DynamicPydanticConverter(Converter):

    @staticmethod
    @staticmethod
    def from_obj(cls, obj, **kwargs) -> dict:
        if hasattr(obj, "model_dump"):
            return obj.model_dump(**kwargs)
        return ln.to_dict(obj, **kwargs)

    @staticmethod
    def to_obj(self, **kwargs) -> Any:
        return create_dynamic_pydantic_model(
            self=self,
            model_name="DynamicModel",
            base_cls=BaseModel,
            **kwargs,
        )


class DynamicLionModelConverter(Converter):

    @staticmethod
    def from_obj(cls, obj, **kwargs) -> dict:
        return obj.to_dict(**kwargs)

    @staticmethod
    def to_obj(self, **kwargs) -> Any:
        return create_dynamic_pydantic_model(self=self, **kwargs)


def create_dynamic_pydantic_model(
    self: Component,
    model_name: str = None,
    base_cls: BaseModel = None,
    **kwargs,
) -> Any:
    config = self.all_fields
    cls_kwargs = {}
    for k, v in self.all_fields.items():
        config[k] = (v.annotation, v)
        cls_kwargs[k] = getattr(self, k)
    config["__cls_kwargs__"] = cls_kwargs
    config["__base__"] = base_cls or self.__class__
    model_name = model_name or f"Dynamic{self.class_name()}"
    kwargs = {**config, **kwargs}
    return create_model(model_name, **kwargs)
