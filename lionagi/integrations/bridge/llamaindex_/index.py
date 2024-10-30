from lionfuncs import check_import


class LlamaIndex:

    llama_index = check_import("llama_index", pip_name="llama-index")

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
        Settings = check_import("llama_index.core", import_name="Settings")
        OpenAI = check_import("llama_index.llms.openai", import_name="OpenAI")

        if not llm_obj:
            llm_class = llm_class or OpenAI
            llm_kwargs = llm_kwargs or {}
            if "model" not in llm_kwargs:
                llm_kwargs["model"] = "gpt-4o"
            llm_obj = llm_class(**llm_kwargs)

        Settings.llm = llm_obj

        if not index_type:
            VectorStoreIndex = check_import(
                "llama_index.core", import_name="VectorStoreIndex"
            )
            index_type = VectorStoreIndex

        return index_type(nodes, **kwargs)
