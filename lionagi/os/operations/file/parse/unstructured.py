from typing import Any, Callable, List, Optional, Dict
import pandas as pd


class UnstructuredElementNodeParser:
    """Unstructured element node parser.

    Splits a document into Text Nodes and Index Nodes corresponding to embedded objects
    (e.g. tables).
    """

    def __init__(
        self,
        llm: Optional[Any] = None,
        summary_query_str: str = "DEFAULT_SUMMARY_QUERY_STR",
        partitioning_parameters: Optional[Dict[str, Any]] = None,
    ):
        self.llm = llm
        self.summary_query_str = summary_query_str
        self.partitioning_parameters = partitioning_parameters or {}

    @classmethod
    def class_name(cls) -> str:
        return "UnstructuredElementNodeParser"

    async def get_nodes_from_node(self, node: Component) -> List[Component]:
        """Get nodes from node."""
        elements = self.extract_elements(
            node.content, table_filters=[self.filter_table]
        )
        table_elements = self.get_table_elements(elements)
        await self.aextract_table_summaries(table_elements)
        nodes = self.get_nodes_from_elements(elements, node, ref_doc_text=node.content)
        self._update_node_relationships(node, nodes)
        return nodes

    def extract_elements(
        self, text: str, table_filters: Optional[List[Callable]] = None, **kwargs: Any
    ) -> List[Part]:
        """Extract elements from text."""
        from unstructured.partition.html import partition_html

        table_filters = table_filters or []
        elements = partition_html(text=text, **self.partitioning_parameters)
        return self._process_elements(elements, table_filters)

    def filter_table(self, table_element: Any) -> bool:
        """Filter tables."""
        table_df = html_to_df(table_element.metadata.text_as_html)
        return table_df is not None and not table_df.empty and len(table_df.columns) > 1

    def _process_elements(
        self, elements: List[Any], table_filters: List[Callable]
    ) -> List[Part]:
        output_parts = []
        for idx, element in enumerate(elements):
            part = self._create_part(idx, element, table_filters)
            output_parts.append(part)
        return output_parts

    def _create_part(
        self, idx: int, element: Any, table_filters: List[Callable]
    ) -> Part:
        if "unstructured.documents.html.HTMLTable" in str(type(element)):
            return self._create_table_part(idx, element, table_filters)
        return Part(id=f"id_{idx}", type="text", content=element)

    def _create_table_part(
        self, idx: int, element: Any, table_filters: List[Callable]
    ) -> Part:
        should_keep = all(tf(element) for tf in table_filters)
        if should_keep:
            table_df = html_to_df(str(element.metadata.text_as_html))
            return Part(id=f"id_{idx}", type="table", content=element, table=table_df)
        from unstructured.documents.html import HTMLText

        new_element = HTMLText(str(element), tag=element.tag)
        return Part(id=f"id_{idx}", type="text", content=new_element)

    def get_table_elements(self, parts: List[Part]) -> List[Part]:
        return [e for e in parts if e.type == "table"]

    def get_nodes_from_elements(
        self, parts: List[Part], node: Component, ref_doc_text: str
    ) -> List[Component]:
        components = []
        for part in parts:
            component = Component(id=part.id, content=part.content)
            components.append(component)
        return components

    def _update_node_relationships(
        self, node: Component, nodes: List[Component]
    ) -> None:
        source_document = node.as_related_node_info()
        for n in nodes:
            n.relationships["source"] = source_document
            n.metadata.update(node.metadata)

    async def extract_table_summaries(self, parts: List[Part]) -> None:
        """Table summaries extraction placeholder."""
        pass


# Example usage
# parser = UnstructuredElementNodeParser()
# component = Component(id="node1", content="<html>Some HTML content</html>")
# nodes = parser.get_nodes_from_node(component)
