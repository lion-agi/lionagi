from abc import ABC
from pydantic import BaseModel, Field, AliasChoices
from lionagi.os.lib.sys_util import create_id, get_timestamp


_init_class = {}


class Element(BaseModel, ABC):
    """Base class for elements within the LionAGI system.

    Attributes:
        ln_id (str): A 32-char unique hash identifier.
        timestamp (str): The UTC timestamp of creation.
    """

    ln_id: str = Field(
        default_factory=create_id,
        title="ID",
        description="A 32-char unique hash identifier.",
        frozen=True,
        validation_alias=AliasChoices("node_id", "ID", "id"),
    )

    timestamp: str = Field(
        default_factory=lambda: get_timestamp(sep=None)[:-6],
        title="Creation Timestamp",
        description="The UTC timestamp of creation",
        frozen=True,
        alias="created",
        validation_alias=AliasChoices("created_on", "creation_date"),
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in _init_class:
            _init_class[cls.__name__] = cls

    @property
    def class_name(self) -> str:
        """Get the class name."""
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        """Get the class name."""
        return cls.__name__
    
    # element is always true
    def __bool__(self):
        return True
