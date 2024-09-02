from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LlamaIndex:

    @classmethod
    def index(
        cls,
        nodes,
        llm_obj=None,
        llm_class=None,
        llm_kwargs=None,
        index_type=None,
        **kwargs,
    ):
        from llama_index.core import Settings
        from llama_index.llms.openai import OpenAI

        if not llm_obj:
            llm_class = llm_class or OpenAI
            llm_kwargs = llm_kwargs or {}
            if "model" not in llm_kwargs:
                llm_kwargs["model"] = "gpt-4o"
            llm_obj = llm_class(**llm_kwargs)

        Settings.llm = llm_obj

        if not index_type:
            from llama_index.core import VectorStoreIndex

            index_type = VectorStoreIndex

        return index_type(nodes, **kwargs)
