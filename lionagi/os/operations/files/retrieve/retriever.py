from abc import ABC, abstractmethod
from typing import Any, List, Optional, Callable, Dict, Tuple, Union
import logging

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union


class RetrievalInterface(ABC):
    @abstractmethod
    def retrieve(
        self, query: str, strategy: str, method: str, context: Optional[str] = None
    ) -> Any:
        """Retrieve information based on the query, strategy, method, and context."""
        pass


# Base Retriever
class BaseRetriever(ABC):
    """Base retriever class providing common functionality."""

    def __init__(self, logger: Optional[Any] = None):
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def retrieve(self, query: str) -> List[Any]:
        """Retrieve nodes based on the query."""
        pass

    def log(self, message: str):
        """Log a message."""
        self.logger.info(message)


# Graph Retriever (Base)
class BaseGraphRetriever(BaseRetriever):
    def __init__(self, imodel: Optional[Any] = None, logger: Optional[Any] = None):
        super().__init__(logger)
        self.imodel = imodel

    @abstractmethod
    async def retrieve(self, query_bundle: Any) -> List[Any]:
        pass


# Tree Retriever (Graph)
class TreeRetriever(BaseGraphRetriever):
    def __init__(self, tree: Any, **kwargs):
        super().__init__(**kwargs)
        self.tree = tree

    def retrieve(self, query: str) -> List[Any]:
        self.log(f"Starting query: {query}")
        # Pseudocode: Retrieve all leaf nodes from the tree
        leaf_nodes = [node for node in self.tree.nodes if not node.relations["out"]]
        return leaf_nodes


# Knowledge Graph Retriever (Graph)
class KnowledgeGraphRetriever(BaseGraphRetriever):
    """Retriever for querying the knowledge graph."""

    def __init__(
        self,
        index: Any,
        imodel: Any,
        embed_model: Any = None,
        retriever_mode: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(imodel)
        self.index = index
        self.embed_model = embed_model
        self.retriever_mode = retriever_mode

    def retrieve(self, query: str) -> List[Any]:
        self.log(f"Starting query: {query}")
        if self.retriever_mode == "embedding":
            return self._retrieve_by_embedding(query)
        else:
            return self._retrieve_by_text(query)

    def _retrieve_by_text(self, query: str) -> List[Any]:
        matched_nodes = []
        for node in self.index._index_struct.nodes:
            if query.lower() in node.get_content().lower():
                matched_nodes.append(node)
        return matched_nodes

    def _retrieve_by_embedding(self, query: str) -> List[Any]:
        query_embedding = self.embed_model.get_text_embedding(query)
        scores = []
        for (
            node_text,
            node_embedding,
        ) in self.index._index_struct.embedding_dict.items():
            score = self.embed_model.compute_similarity(query_embedding, node_embedding)
            scores.append((node_text, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        top_matches = [
            self.index._index_struct.get_node_by_content(text)
            for text, _ in scores[:10]
        ]
        return top_matches


# Table Retriever
class TableRetriever(BaseGraphRetriever):
    def __init__(self, graph_store: Any, **kwargs):
        super().__init__(**kwargs)
        self.graph_store = graph_store
        self.query_keyword_extract_template = kwargs.get(
            "query_keyword_extract_template"
        )
        self.max_keywords_per_query = kwargs.get("max_keywords_per_query", 10)
        self.num_chunks_per_query = kwargs.get("num_chunks_per_query", 10)
        self.include_text = kwargs.get("include_text", True)
        self.retriever_mode = kwargs.get("retriever_mode", "keyword")
        self.similarity_top_k = kwargs.get("similarity_top_k", 2)
        self.graph_store_query_depth = kwargs.get("graph_store_query_depth", 2)
        self.use_global_node_triplets = kwargs.get("use_global_node_triplets", False)
        self.max_knowledge_sequence = kwargs.get("max_knowledge_sequence", 30)
        self.llm = kwargs.get("llm")
        self.embed_model = kwargs.get("embed_model")

    def retrieve(self, query_bundle: Any) -> List[Any]:
        self.log(f"Starting query: {query_bundle.query_str}")
        # Pseudocode: Retrieve nodes based on keywords and/or embeddings
        nodes = []
        if self.retriever_mode in ["keyword", "hybrid"]:
            nodes.extend(self._retrieve_by_keywords(query_bundle))
        if self.retriever_mode in ["embedding", "hybrid"]:
            nodes.extend(self._retrieve_by_embeddings(query_bundle))
        return nodes

    def _retrieve_by_keywords(self, query_bundle: Any) -> List[Any]:
        # Pseudocode: Extract keywords, perform keyword-based search, and get related nodes
        keywords = self._extract_keywords(query_bundle.query_str)
        self.log(f"Extracted keywords: {keywords}")
        rel_texts = self._search_keywords_in_graph_store(keywords)
        nodes = self._get_nodes_from_texts(rel_texts)
        return nodes

    def _retrieve_by_embeddings(self, query_bundle: Any) -> List[Any]:
        # Pseudocode: Get embedding for the query and retrieve nodes based on similarity
        query_embedding = self.embed_model.get_text_embedding(query_bundle.query_str)
        nodes = self._search_embeddings_in_graph_store(query_embedding)
        return nodes

    def _extract_keywords(self, query_str: str) -> List[str]:
        response = self.llm.predict(
            self.query_keyword_extract_template,
            max_keywords=self.max_keywords_per_query,
            question=query_str,
        )
        return self._parse_keywords(response)

    def _parse_keywords(self, response: str) -> List[str]:
        keywords = []
        for line in response.split("\n"):
            if line.startswith("KEYWORDS:"):
                keywords = line.replace("KEYWORDS:", "").strip().split(",")
                break
        return [kw.strip() for kw in keywords]

    def _search_keywords_in_graph_store(self, keywords: List[str]) -> List[str]:
        # Pseudocode: Search graph store using keywords and return related texts
        rel_texts = []
        for keyword in keywords:
            node_ids = self.graph_store.search_node_by_keyword(keyword)
            for node_id in node_ids:
                node = self.graph_store.get_node(node_id)
                rel_texts.append(node.get_content())
        return rel_texts

    def _search_embeddings_in_graph_store(self, query_embedding: Any) -> List[Any]:
        # Pseudocode: Perform embedding-based search in the graph store and return related nodes
        nodes = []
        similarities, top_rel_texts = self._get_top_k_embeddings(query_embedding)
        for text in top_rel_texts:
            node = self.graph_store.get_node_by_content(text)
            nodes.append(node)
        return nodes

    def _get_top_k_embeddings(
        self, query_embedding: Any
    ) -> Tuple[List[float], List[str]]:
        # Pseudocode: Compute top K embeddings and return similarities and texts
        return [], []

    def _get_nodes_from_texts(self, texts: List[str]) -> List[Any]:
        # Pseudocode: Convert texts to nodes
        nodes = []
        for text in texts:
            node = Node(text)
            nodes.append(node)
        return nodes


# Knowledge Table Retriever (Extends Table Retriever)
class KnowledgeTableRetriever(TableRetriever):
    def retrieve(self, query_bundle: Any) -> List[Any]:
        self.log(f"Starting query: {query_bundle.query_str}")
        # Pseudocode: Retrieve knowledge-specific table data
        knowledge_nodes = super().retrieve(query_bundle)
        # Additional processing for knowledge-specific retrieval
        return knowledge_nodes
