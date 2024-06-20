from typing import TypeVar
from ...generic.exceptions import LionValueError

T = TypeVar("T")


class PydanticComponentMixin:

    @classmethod
    def _from_base_model(cls, obj, /, pydantic_kwargs=None, **kwargs) -> T:
        """Create a node instance from a Pydantic BaseModel."""
        pydantic_kwargs = pydantic_kwargs or {"by_alias": True}
        try:
            config_ = obj.model_dump(**pydantic_kwargs)
        except:
            try:
                if hasattr(obj, "to_dict"):
                    config_ = obj.to_dict(**pydantic_kwargs)
                elif hasattr(obj, "dict"):
                    config_ = obj.dict(**pydantic_kwargs)
                else:
                    raise LionValueError(
                        "Invalid Pydantic model for deserialization: "
                        "missing 'to_dict'(V2) or 'dict'(V1) method."
                    )
            except Exception as e:
                raise LionValueError(
                    f"Invalid Pydantic model for deserialization: {e}"
                ) from e
        return cls.from_obj(config_ | kwargs)
