
### Class: `LlamaPack`

**Description**:
`LlamaPack` is a utility class that provides static methods for downloading and building various Llama packs. Each method represents a different pack and facilitates its download and initialization.

### Methods:

#### Method: `download`

**Signature**:
```python
@staticmethod
def download(pack_name, pack_path)
```

**Description**:
Downloads the specified Llama pack.

**Parameters**:
- `pack_name` (str): The name of the pack to download.
- `pack_path` (str): The path to where the pack should be downloaded.

**Returns**:
- `Any`: The result of the download operation.

**Raises**:
- `ImportError`: If an error occurs during the download.

#### Method: `build`

**Signature**:
```python
@staticmethod
def build(pack_name, pack_path, args=[], **kwargs)
```

**Description**:
Builds the specified Llama pack using the provided arguments.

**Parameters**:
- `pack_name` (str): The name of the pack to build.
- `pack_path` (str): The path to the downloaded pack.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The result of the build operation.

#### Method: `stock_market_pack`

**Signature**:
```python
@staticmethod
def stock_market_pack(pack_path="./stock_market_data_pack", args=[], **kwargs)
```

**Description**:
Builds the Stock Market Data Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./stock_market_data_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `embedded_table_pack`

**Signature**:
```python
@staticmethod
def embedded_table_pack(pack_path="./embedded_tables_unstructured_pack", args=[], **kwargs)
```

**Description**:
Builds the Recursive Retriever Small to Big Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./embedded_tables_unstructured_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `rag_evaluator_pack`

**Signature**:
```python
@staticmethod
def rag_evaluator_pack(pack_path="./rag_evaluator_pack", args=[], **kwargs)
```

**Description**:
Builds the Rag Evaluator Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./rag_evaluator_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `ollma_pack`

**Signature**:
```python
@staticmethod
def ollma_pack(pack_path="./ollama_pack", args=[], **kwargs)
```

**Description**:
Builds the Ollama Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./ollama_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `llm_compiler_agent_pack`

**Signature**:
```python
@staticmethod
def llm_compiler_agent_pack(pack_path="./llm_compiler_agent_pack", args=[], **kwargs)
```

**Description**:
Builds the LLM Compiler Agent Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./llm_compiler_agent_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `resume_screener_pack`

**Signature**:
```python
@staticmethod
def resume_screener_pack(pack_path="./resume_screener_pack", args=[], **kwargs)
```

**Description**:
Builds the Resume Screener Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./resume_screener_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `ragatouille_retriever_pack`

**Signature**:
```python
@staticmethod
def ragatouille_retriever_pack(pack_path="./ragatouille_pack", args=[], **kwargs)
```

**Description**:
Builds the RAGatouille Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./ragatouille_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `chain_of_table_pack`

**Signature**:
```python
@staticmethod
def chain_of_table_pack(pack_path="./chain_of_table_pack", args=[], **kwargs)
```

**Description**:
Builds the Chain of Table Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./chain_of_table_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `hybrid_fusion_retriever_pack`

**Signature**:
```python
@staticmethod
def hybrid_fusion_retriever_pack(pack_path="./hybrid_fusion_pack", args=[], **kwargs)
```

**Description**:
Builds the Hybrid Fusion Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./hybrid_fusion_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `neo4j_query_engine_pack`

**Signature**:
```python
@staticmethod
def neo4j_query_engine_pack(pack_path="./neo4j_pack", args=[], **kwargs)
```

**Description**:
Builds the Neo4j Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./neo4j_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `llava_completion_pack`

**Signature**:
```python
@staticmethod
def llava_completion_pack(pack_path="./llava_pack", args=[], **kwargs)
```

**Description**:
Builds the Llava Completion Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./llava_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `sentence_window_retriever_pack`

**Signature**:
```python
@staticmethod
def sentence_window_retriever_pack(pack_path="./sentence_window_retriever_pack", args=[], **kwargs)
```

**Description**:
Builds the Sentence Window Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./sentence_window_retriever_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `dense_x_retrieval_pack`

**Signature**:
```python
@staticmethod
def dense_x_retrieval_pack(pack_path="./dense_pack", args=[], **kwargs)
```

**Description**:
Builds the Dense X Retrieval Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./dense_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `zephyr_query_engine_pack`

**Signature**:
```python
@staticmethod
def zephyr_query_engine_pack(pack_path="./zephyr_pack", args=[], **kwargs)
```

**Description**:
Builds the Zephyr Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./zephyr_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized

 pack.

#### Method: `query_rewriting_retriever_pack`

**Signature**:
```python
@staticmethod
def query_rewriting_retriever_pack(pack_path="./query_rewriting_pack", args=[], **kwargs)
```

**Description**:
Builds the Query Rewriting Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./query_rewriting_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `fuzzy_citation_engine_pack`

**Signature**:
```python
@staticmethod
def fuzzy_citation_engine_pack(pack_path="./fuzzy_citation_pack", args=[], **kwargs)
```

**Description**:
Builds the Fuzzy Citation Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./fuzzy_citation_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `multidoc_auto_retriever_pack`

**Signature**:
```python
@staticmethod
def multidoc_auto_retriever_pack(pack_path="./multidoc_autoretrieval_pack", args=[], **kwargs)
```

**Description**:
Builds the MultiDoc Auto Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./multidoc_autoretrieval_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `auto_merging_retriever_pack`

**Signature**:
```python
@staticmethod
def auto_merging_retriever_pack(pack_path="./auto_merging_retriever_pack", args=[], **kwargs)
```

**Description**:
Builds the Auto Merging Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./auto_merging_retriever_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `voyage_query_engine_pack`

**Signature**:
```python
@staticmethod
def voyage_query_engine_pack(pack_path="./voyage_pack", args=[], **kwargs)
```

**Description**:
Builds the Voyage Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./voyage_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `mix_self_consistency_pack`

**Signature**:
```python
@staticmethod
def mix_self_consistency_pack(pack_path="./mix_self_consistency_pack", args=[], **kwargs)
```

**Description**:
Builds the Mix Self Consistency Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./mix_self_consistency_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `rag_fusion_pipeline_pack`

**Signature**:
```python
@staticmethod
def rag_fusion_pipeline_pack(pack_path="./rag_fusion_pipeline_pack", args=[], **kwargs)
```

**Description**:
Builds the RAG Fusion Pipeline Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./rag_fusion_pipeline_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `multi_document_agents_pack`

**Signature**:
```python
@staticmethod
def multi_document_agents_pack(pack_path="./multi_doc_agents_pack", args=[], **kwargs)
```

**Description**:
Builds the Multi Document Agents Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./multi_doc_agents_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `llama_guard_moderator_pack`

**Signature**:
```python
@staticmethod
def llama_guard_moderator_pack(pack_path="./llamaguard_pack", args=[], **kwargs)
```

**Description**:
Builds the Llama Guard Moderator Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./llamaguard_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `evaluator_benchmarker_pack`

**Signature**:
```python
@staticmethod
def evaluator_benchmarker_pack(pack_path="./eval_benchmark_pack", args=[], **kwargs)
```

**Description**:
Builds the Evaluator Benchmarker Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./eval_benchmark_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `amazon_product_extraction_pack`

**Signature**:
```python
@staticmethod
def amazon_product_extraction_pack(pack_path="./amazon_product_extraction_pack", args=[], **kwargs)
```

**Description**:
Builds the Amazon Product Extraction Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./amazon_product_extraction_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `llama_dataset_metadata_pack`

**Signature**:
```python
@staticmethod
def llama_dataset_metadata_pack(pack_path="./llama_dataset_metadata_pack", args=[], **kwargs)
```

**Description**:
Builds the Llama Dataset Metadata Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./llama_dataset_metadata_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `multi_tenancy_rag_pack`

**Signature**:
```python
@staticmethod
def multi_tenancy_rag_pack(pack_path="./multitenancy_rag_pack", args=[], **kwargs)
```

**Description**:
Builds the Multi Tenancy RAG Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./multitenancy_rag_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `gmail_openai_agent_pack`

**Signature**:
```python
@staticmethod
def gmail_openai_agent_pack(pack_path="./gmail_pack", args=[], **kwargs)
```

**Description**:
Builds the Gmail OpenAI Agent Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./gmail_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `snowflake_query_engine_pack`

**Signature**:
```python
@staticmethod
def snowflake_query_engine_pack(pack_path="./snowflake_pack", args=[], **kwargs)
```

**Description**:
Builds the Snowflake Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./snowflake_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `agent_search_retriever_pack`

**Signature**:
```python
@staticmethod
def agent_search_retriever_pack(pack_path="./agent_search_pack", args=[], **kwargs)
```

**Description**:
Builds the Agent Search Retriever Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./agent_search_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
-

 `Any`: The initialized pack.

#### Method: `vectara_rag_pack`

**Signature**:
```python
@staticmethod
def vectara_rag_pack(pack_path="./vectara_rag_pack", args=[], **kwargs)
```

**Description**:
Builds the Vectara RAG Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./vectara_rag_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `chroma_autoretrieval_pack`

**Signature**:
```python
@staticmethod
def chroma_autoretrieval_pack(pack_path="./chroma_pack", args=[], **kwargs)
```

**Description**:
Builds the Chroma Autoretrieval Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./chroma_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `arize_phoenix_query_engine_pack`

**Signature**:
```python
@staticmethod
def arize_phoenix_query_engine_pack(pack_path="./arize_pack", args=[], **kwargs)
```

**Description**:
Builds the Arize Phoenix Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./arize_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `redis_ingestion_pipeline_pack`

**Signature**:
```python
@staticmethod
def redis_ingestion_pipeline_pack(pack_path="./redis_ingestion_pack", args=[], **kwargs)
```

**Description**:
Builds the Redis Ingestion Pipeline Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./redis_ingestion_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `nebula_graph_query_engine_pack`

**Signature**:
```python
@staticmethod
def nebula_graph_query_engine_pack(pack_path="./nebulagraph_pack", args=[], **kwargs)
```

**Description**:
Builds the Nebula Graph Query Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./nebulagraph_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.

#### Method: `weaviate_retry_engine_pack`

**Signature**:
```python
@staticmethod
def weaviate_retry_engine_pack(pack_path="./weaviate_pack", args=[], **kwargs)
```

**Description**:
Builds the Weaviate Retry Engine Pack.

**Parameters**:
- `pack_path` (str, optional): The path to the pack. Defaults to `./weaviate_pack`.
- `args` (list, optional): Positional arguments for the pack.
- `kwargs` (dict, optional): Keyword arguments for the pack.

**Returns**:
- `Any`: The initialized pack.
