from abc import ABC
from typing import Any

from lionagi.core.schema.base.base_mixin import BaseComponentMixin
from lionagi.core.schema.base_node import T
from lionagi.integrations.bridge.pydantic_ import base_model as pyd
from lionagi.libs.sys_util import SysUtil


class BaseComponent(BaseComponentMixin, ABC):
    """
    A base component model that provides common attributes and utility methods for metadata management.
    It includes functionality to interact with metadata in various ways, such as retrieving, modifying,
    and validating metadata keys and values.

    Attributes:
        id_ (str): Unique identifier, defaulted using SysUtil.create_id.
        timestamp (str | None): Timestamp of creation or modification.
        metadata (dict[str, Any]): Metadata associated with the component.
    """

    id_: str = pyd.ln_Field(default_factory=SysUtil.create_id, alias="node_id")
    timestamp: str | None = pyd.ln_Field(default_factory=SysUtil.get_timestamp)
    metadata: dict[str, Any] = pyd.ln_Field(default_factory=dict, alias="meta")

    class Config:
        """Model configuration settings."""

        extra = "allow"
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    def copy(self, *args, **kwargs) -> T:
        """
        Creates a deep copy of the instance, with an option to update specific fields.

        Args:
            *args: Variable length argument list for additional options.
            **kwargs: Arbitrary keyword arguments specifying updates to the instance.

        Returns:
            BaseComponent: A new instance of BaseComponent as a deep copy of the original, with updates applied.
        """
        return self.model_copy(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"
