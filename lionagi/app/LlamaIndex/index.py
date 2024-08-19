from typing import Type, Any

from lionagi.os.primitives import Node, Pile
from lionagi.os.sys_util import SysUtil
from .config import DEFAULT_MODEL


def create_llamaindex(
    nodes: list | Pile | Any,
    *args,  # additional index init args
    index_type: Type | None = None,
    llm=None,
    model_config: dict = None,
    return_llama_nodes=False,
    **kwargs,  # additional index init kwargs
):
    Settings = SysUtil.check_import(
        package_name="llama_index",
        module_name="core",
        import_name="Settings",
        pip_name="llama-index",
    )

    if not llm:
        OpenAI = SysUtil.import_module(
            package_name="llama_index",
            module_name="llms.openai",
            import_name="OpenAI",
        )
        config = {**(model_config or {})}
        config["model"] = config.pop("model", DEFAULT_MODEL)
        llm = OpenAI(**config)

    Settings.llm = llm

    if not index_type:
        VectorStoreIndex = SysUtil.import_module(
            package_name="llama_index",
            module_name="core",
            import_name="VectorStoreIndex",
        )

        index_type = VectorStoreIndex

    if isinstance(nodes, Pile):
        nodes = list(nodes)

    if not isinstance(nodes, list):
        nodes = [nodes]

    _nodes = []
    for i in nodes:
        if isinstance(i, Node):
            i = i.convert_to("llamaindex")
        _nodes.append(i)

    out = index_type(_nodes, *args, **kwargs)
    if return_llama_nodes:
        return out, _nodes
    return out
