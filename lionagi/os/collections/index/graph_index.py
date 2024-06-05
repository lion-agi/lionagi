# from .index import Index
# from ..node.node import Node

# import logging
# from typing import Any, Dict, Optional, Sequence

# logger = logging.getLogger(__name__)


# class GraphIndex(Index):
#     """Knowledge Graph Index for managing and querying knowledge graphs."""

#     def __init__(
#         self,
#         nodes=None,
#         objects=None,
#         index_struct=None,
#         show_progress: bool = False,
#         max_object_length: int = 128,
#         **kwargs: Any,
#     ) -> None:
#         """Initialize the KnowledgeGraphIndex."""
#         self.include_embeddings = kwargs.get("include_embeddings", False)
#         self.max_object_length = max_object_length

#         super().__init__(
#             nodes=nodes,
#             index_struct=index_struct,
#             show_progress=show_progress,
#             objects=objects,
#             **kwargs,
#         )

#     def as_retriever(
#         self,
#         retriever_mode: Optional[str] = None,
#         embed_model: Optional[BaseEmbedding] = None,
#         **kwargs: Any,
#     ) -> BaseRetriever:
#         """Return a retriever based on the specified mode."""
#         return KnowledgeGraphRetriever(
#             self,
#             llm=self._llm,
#             embed_model=embed_model or self._embed_model,
#             retriever_mode=retriever_mode,
#             **kwargs,
#         )

#     def _build_index_from_nodes(self, nodes: Sequence[Node]) -> KG:
#         """Build the index from nodes."""
#         index_struct = self.index_struct_cls()
#         nodes_with_progress = get_tqdm_iterable(
#             nodes, self._show_progress, "Processing nodes"
#         )
#         for node in nodes_with_progress:
#             index_struct.add_node(node.keywords, node)
#             if self.include_embeddings:
#                 node_texts = [node.get_content(metadata_mode=MetadataMode.LLM)]
#                 embed_outputs = self._embed_model.get_text_embedding_batch(node_texts)
#                 for text, embed in zip(node_texts, embed_outputs):
#                     index_struct.add_to_embedding_dict(text, embed)
#         return index_struct

#     def _insert(self, nodes: Sequence[Node], **insert_kwargs: Any) -> None:
#         """Insert nodes into the index."""
#         for node in nodes:
#             self._index_struct.add_node(node.keywords, node)
#             if self.include_embeddings:
#                 node_text = node.get_content(metadata_mode=MetadataMode.LLM)
#                 if node_text not in self._index_struct.embedding_dict:
#                     embedding = self._embed_model.get_text_embedding(node_text)
#                     self._index_struct.add_to_embedding_dict(node_text, embedding)

#     def delete_node(self, node_id: str, **delete_kwargs: Any) -> None:
#         """Delete a node."""
#         self._index_struct.delete_node(node_id)

#     @property
#     def ref_doc_info(self) -> Dict[str, RefDocInfo]:
#         """Retrieve a dict mapping of ingested documents and their nodes+metadata."""
#         node_doc_ids = self._index_struct.get_all_node_ids()
#         nodes = self.docstore.get_nodes(node_doc_ids)
#         return {node.node_id: node.ref_doc_info for node in nodes}

#     def get_networkx_graph(self, limit: int = 100) -> Any:
#         """Get networkx representation of the graph structure."""
#         try:
#             import networkx as nx
#         except ImportError:
#             raise ImportError(
#                 "Please install networkx to visualize the graph: `pip install networkx`"
#             )

#         g = nx.Graph()
#         for node in self._index_struct.nodes[:limit]:
#             g.add_node(node.node_id, label=node.get_content())
#             for related_node_id in node.related_nodes:
#                 g.add_edge(node.node_id, related_node_id)
#         return g

#     @property
#     def query_context(self) -> Dict[str, Any]:
#         """Return the query context."""
#         return {"index_struct": self._index_struct}
