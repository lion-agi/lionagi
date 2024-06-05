from typing import Any, Dict, List, Optional, Sequence


class HTMLNodeParser:
    """HTML node parser.

    Splits a document into Nodes using custom HTML splitting logic.
    """

    def __init__(
        self,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        tags: Optional[List[str]] = None,
    ):
        self.include_metadata = include_metadata
        self.include_prev_next_rel = include_prev_next_rel
        self.tags = tags or [
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "b",
            "i",
            "u",
            "section",
        ]

    @classmethod
    def from_defaults(
        cls,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        tags: Optional[List[str]] = None,
    ) -> "HTMLNodeParser":
        return cls(
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            tags=tags,
        )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "HTMLNodeParser"

    def parse_nodes(
        self, nodes: Sequence[Any], show_progress: bool = False, **kwargs: Any
    ) -> List[Any]:
        all_nodes: List[Any] = []
        nodes_with_progress = get_progress_iterable(
            nodes, show_progress, "Parsing nodes"
        )

        for node in nodes_with_progress:
            parsed_nodes = self._get_nodes_from_node(node)
            all_nodes.extend(parsed_nodes)

        return all_nodes

    def _get_nodes_from_node(self, node: Any) -> List[Any]:
        """Get nodes from document."""
        text = node.get_content(metadata_mode=MetadataMode.NONE)
        soup = BeautifulSoup(text, "html.parser")
        html_nodes = []
        last_tag = None
        current_section = ""

        tags = soup.find_all(self.tags)
        for tag in tags:
            tag_text = extract_text_from_tag(tag, self.tags)
            if tag.name == last_tag or last_tag is None:
                last_tag = tag.name
                current_section += f"{tag_text.strip()}\n"
            else:
                html_nodes.append(
                    build_node_from_split(
                        current_section.strip(),
                        node,
                        {"tag": last_tag},
                        self.include_metadata,
                    )
                )
                last_tag = tag.name
                current_section = f"{tag_text}\n"

        if current_section:
            html_nodes.append(
                build_node_from_split(
                    current_section.strip(),
                    node,
                    {"tag": last_tag},
                    self.include_metadata,
                )
            )

        return html_nodes
