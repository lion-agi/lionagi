import logging
from typing import Any, Dict, List, Optional, Sequence
from tqdm import tqdm
from .base import Parser


class HierarchicalParser(Parser):
    """Hierarchical node parser.

    Splits a document into a recursive hierarchy of Components using a Parser.

    This returns a hierarchy of nodes in a flat list, with overlap between parent nodes
    and child nodes per parent.
    """

    def __init__(
        self,
        chunk_sizes: Optional[List[int]] = None,
        node_parser_ids: Optional[List[str]] = None,
        node_parser_map: Optional[Dict[str, "Parser"]] = None,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
    ):
        self.chunk_sizes = chunk_sizes
        self.node_parser_ids = node_parser_ids or []
        self.node_parser_map = node_parser_map or {}
        self.include_metadata = include_metadata
        self.include_prev_next_rel = include_prev_next_rel

    @classmethod
    def from_defaults(
        cls,
        chunk_sizes: Optional[List[int]] = None,
        chunk_overlap: int = 20,
        node_parser_ids: Optional[List[str]] = None,
        node_parser_map: Optional[Dict[str, "Parser"]] = None,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
    ) -> "HierarchicalParser":
        if node_parser_ids is None:
            if chunk_sizes is None:
                chunk_sizes = [2048, 512, 128]

            node_parser_ids = [f"chunk_size_{chunk_size}" for chunk_size in chunk_sizes]
            node_parser_map = {}
            for chunk_size, node_parser_id in zip(chunk_sizes, node_parser_ids):
                node_parser_map[node_parser_id] = Parser(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    include_metadata=include_metadata,
                    include_prev_next_rel=include_prev_next_rel,
                )
        else:
            if chunk_sizes is not None:
                raise ValueError("Cannot specify both node_parser_ids and chunk_sizes.")
            if node_parser_map is None:
                raise ValueError(
                    "Must specify node_parser_map if using node_parser_ids."
                )

        return cls(
            chunk_sizes=chunk_sizes,
            node_parser_ids=node_parser_ids,
            node_parser_map=node_parser_map,
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
        )

    @classmethod
    def class_name(cls) -> str:
        return "HierarchicalParser"

    def _split_nodes(
        self, nodes: List[Component], level: int, show_progress: bool
    ) -> List[Component]:
        """Split nodes into sub-nodes."""
        nodes_with_progress = self.get_tqdm_iterable(
            nodes, show_progress, "Parsing documents into nodes"
        )
        sub_nodes = []
        for node in nodes_with_progress:
            cur_sub_nodes = self.node_parser_map[
                self.node_parser_ids[level]
            ].get_nodes_from_documents([node])
            if level > 0:
                self._add_relationships(node, cur_sub_nodes)
            sub_nodes.extend(cur_sub_nodes)
        return sub_nodes

    def _add_relationships(
        self, parent_node: Component, child_nodes: List[Component]
    ) -> None:
        """Add parent-child relationships between nodes."""
        for child_node in child_nodes:
            child_list = parent_node.relationships.get("child", [])
            child_list.append(child_node.as_related_node_info())
            parent_node.relationships["child"] = child_list

            child_node.relationships["parent"] = parent_node.as_related_node_info()

    def _recursively_get_nodes(
        self, nodes: List[Component], level: int, show_progress: bool
    ) -> List[Component]:
        """Recursively get nodes from nodes."""
        if level >= len(self.node_parser_ids):
            raise ValueError(
                f"Level {level} is greater than number of text splitters ({len(self.node_parser_ids)})."
            )

        sub_nodes = self._split_nodes(nodes, level, show_progress)

        if level < len(self.node_parser_ids) - 1:
            sub_sub_nodes = self._recursively_get_nodes(
                sub_nodes, level + 1, show_progress
            )
        else:
            sub_sub_nodes = []

        return sub_nodes + sub_sub_nodes

    def get_nodes_from_documents(
        self, documents: Sequence[Any], show_progress: bool = False, **kwargs: Any
    ) -> List[Component]:
        """Parse documents into nodes."""
        all_nodes: List[Component] = []
        documents_with_progress = self.get_tqdm_iterable(
            documents, show_progress, "Parsing documents into nodes"
        )

        for doc in documents_with_progress:
            nodes_from_doc = self._recursively_get_nodes([doc], 0, show_progress)
            all_nodes.extend(nodes_from_doc)

        return all_nodes

    def get_tqdm_iterable(
        self, iterable: Sequence[Any], show_progress: bool, desc: str
    ) -> Sequence[Any]:
        return tqdm(iterable, desc=desc) if show_progress else iterable
