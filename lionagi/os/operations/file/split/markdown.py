import re
from typing import List

# Placeholder for the base splitter class (to be defined according to your specific base class requirements)
class BaseSplitter:
    def __init__(self, chunk_size: int = 100, chunk_overlap: float = 0.1):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_documents(self, texts: List[str]) -> List[List[str]]:
        documents = [self.split_text(text) for text in texts]
        return documents

class RecursiveMarkdownSplitter(BaseSplitter):
    def __init__(self, separators: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.separators = separators or [
            r"\n# ",
            r"\n## ",
            r"\n### ",
            r"\n#### ",
            r"\n##### ",
            r"\n###### ",
        ]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        for sep in separators:
            if re.search(re.escape(sep), text):
                separator = sep
                new_separators = separators[separators.index(sep) + 1 :]
                break

        splits = re.split(re.escape(separator), text)
        good_splits = []
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    final_chunks.extend(self._merge_splits(good_splits))
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text(s, new_separators))
        if good_splits:
            final_chunks.extend(self._merge_splits(good_splits))
        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self.separators)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append("".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append("".join(current_chunk))

        return merged_splits

import re
from typing import Any, Dict, List, Optional, Sequence

class MarkdownNodeParser:
    """Markdown node parser.

    Splits a document into Nodes using custom Markdown splitting logic.

    Args:
        include_metadata (bool): whether to include metadata in nodes
        include_prev_next_rel (bool): whether to include prev/next relationships

    """
    
    def __init__(self, include_metadata: bool = True, include_prev_next_rel: bool = True):
        self.include_metadata = include_metadata
        self.include_prev_next_rel = include_prev_next_rel

    def _parse_nodes(
        self,
        nodes: Sequence[Dict[str, Any]],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        all_nodes: List[Dict[str, Any]] = []

        for node in nodes:
            parsed_nodes = self.get_nodes_from_node(node)
            all_nodes.extend(parsed_nodes)

        return all_nodes

    def get_nodes_from_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get nodes from document."""
        text = node["content"]
        markdown_nodes = []
        lines = text.split("\n")
        metadata: Dict[str, str] = {}
        code_block = False
        current_section = ""

        for line in lines:
            if line.lstrip().startswith("```"):
                code_block = not code_block
            header_match = re.match(r"^(#+)\s(.*)", line)
            if header_match and not code_block:
                if current_section != "":
                    markdown_nodes.append(
                        self._build_node_from_split(
                            current_section.strip(), node, metadata
                        )
                    )
                metadata = self._update_metadata(
                    metadata, header_match.group(2), len(header_match.group(1).strip())
                )
                current_section = f"{header_match.group(2)}\n"
            else:
                current_section += line + "\n"

        markdown_nodes.append(
            self._build_node_from_split(current_section.strip(), node, metadata)
        )

        return markdown_nodes

    def _update_metadata(
        self, headers_metadata: dict, new_header: str, new_header_level: int
    ) -> dict:
        """Update the markdown headers for metadata.

        Removes all headers that are equal or less than the level
        of the newly found header
        """
        updated_headers = {}

        for i in range(1, new_header_level):
            key = f"Header_{i}"
            if key in headers_metadata:
                updated_headers[key] = headers_metadata[key]

        updated_headers[f"Header_{new_header_level}"] = new_header
        return updated_headers

    def _build_node_from_split(
        self,
        text_split: str,
        node: Dict[str, Any],
        metadata: dict,
    ) -> Dict[str, Any]:
        """Build node from single text split."""
        new_node = {
            "content": text_split,
            "metadata": {**node.get("metadata", {}), **metadata},
            "id": node["id"]
        }
        return new_node
