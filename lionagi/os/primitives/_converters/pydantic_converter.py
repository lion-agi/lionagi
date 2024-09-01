from typing import Any
from pydantic import BaseModel, create_model

from lionagi.os import Converter, lionfuncs as ln
from lionagi.os.primitives.core_types import Component


class DynamicPydanticConverter(Converter):
    _object = "dynamic_pydantic"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: BaseModel, **kwargs: Any) -> dict:
        kwargs["use_model_dump"] = True
        return ln.to_dict(object_, **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: Component, **kwargs: Any) -> dict:
        return ln.to_dict(subject, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subject: Component,
        **kwargs: Any,
    ) -> Any:
        return create_dynamic_pydantic_model(
            self=subject,
            model_name="DynamicModel",
            base_cls=BaseModel,
            **kwargs,
        )


class DynamicLionModelConverter(Converter):
    _object = "dynamic_lion"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: Component, **kwargs: Any) -> dict:
        return ln.to_dict(object_, **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: Component, **kwargs: Any) -> dict:
        return ln.to_dict(subject, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subject: Component,
        **kwargs: Any,
    ) -> Component:
        return create_dynamic_pydantic_model(self=subject, **kwargs)


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
