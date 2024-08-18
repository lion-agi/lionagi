from typing import Any
from lionagi.os.sys_util import SysUtil


def to_llama_index_node(*, node_type: Any = None, **kwargs: Any) -> Any:

    schema = SysUtil.check_import(
        package_name="llama_index",
        module_name="core.schema",
        pip_name="llama-index",
    )
    BaseNode = SysUtil.import_module(
        package_name="llama_index",
        module_name="core.schema",
        import_name="BaseNode",
    )

    node_type = node_type or "TextNode"
    kwargs["text"] = str(kwargs.pop("content", None))
    kwargs["id_"] = kwargs.pop("ln_id", None)

    if not isinstance(node_type, str) and not issubclass(node_type, BaseNode):
        raise TypeError(f"node_type must be a string or BaseNode")

    else:
        try:
            if isinstance(node_type, str) and hasattr(schema, node_type):
                return getattr(schema, node_type).from_dict(kwargs)
            elif issubclass(node_type, BaseNode):
                return node_type.from_dict(kwargs)
            else:
                raise AttributeError(f"Invalid llama-index node type: {node_type}")
        except Exception as e:
            raise AttributeError(f"Error: {e}")
