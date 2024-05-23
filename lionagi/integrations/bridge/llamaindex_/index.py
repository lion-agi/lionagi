
class LlamaIndex:

    @classmethod
    def index(
        cls,
        nodes,
        llm_obj = None, 
        llm_class = None,
        llm_kwargs = None,
        embed=True, 
        embed_model_obj = None,
        embed_model_class = None,
        embed_kwargs = None,
        index_type=None,
        from_storage=False,
        storage_context=None,
        strorage_context_kwargs=None,
        index_id=None,
        load_index_from_storage_kwargs=None,
        **kwargs
    ):
        from llama_index.core import Settings
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
        embed_model = OpenAIEmbedding(model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL)
        
        if not llm_obj:
            llm_class = llm_class or OpenAI
            llm_obj = llm_class(**llm_kwargs or {})
            
        Settings.llm = llm_obj
        
        if embed:
            if not embed_model_obj and not embed_model_class:
                Settings.embed_model = embed_model
            else:
                embed_model_class = embed_model_class or OpenAIEmbedding
                embed_model_obj = embed_model_class(**embed_kwargs or {})
                Settings.embed_model = embed_model_obj
            
        if from_storage:
            from llama_index.core import StorageContext, load_index_from_storage

            storage_context = StorageContext.from_defaults(**strorage_context_kwargs)

            if index_id:
                return load_index_from_storage(
                    storage_context=storage_context,
                    index_id=index_id,
                    **load_index_from_storage_kwargs,
                )
            else:
                raise ValueError("Index ID is required for loading from storage.")

        if not index_type:
            from llama_index.core import VectorStoreIndex
            index_type = VectorStoreIndex
            
        return index_type(nodes, **kwargs)