from typing import Any, Callable, List, Optional, Dict
import pandas as pd


class MarkdownParser:
    """Parser for Markdown formatted documents."""

    @classmethod
    def class_name(cls) -> str:
        return "MarkdownParser"

    def get_components_from_node(self, node: Any) -> List[Component]:
        parts = self.extract_parts(
            node.get_content(), node_id=node.id_, node_metadata=node.metadata
        )
        table_parts = filter_table_parts(parts)
        self.extract_table_summaries(table_parts)
        return self.get_components_from_parts(
            parts, node, ref_doc_text=node.get_content()
        )

    async def aget_components_from_node(self, node: Any) -> List[Component]:
        parts = self.extract_parts(
            node.get_content(), node_id=node.id_, node_metadata=node.metadata
        )
        table_parts = filter_table_parts(parts)
        await self.aextract_table_summaries(table_parts)
        return self.get_components_from_parts(
            parts, node, ref_doc_text=node.get_content()
        )

    def extract_parts(
        self,
        text: str,
        node_id: Optional[str] = None,
        table_filters: Optional[List[Callable]] = None,
        **kwargs: Any,
    ) -> List[Part]:
        parts = []
        lines = text.split("\n")
        current_part = None

        for line in lines:
            if line.startswith("```"):
                current_part = self.handle_code_block(line, current_part, parts)
            elif current_part and current_part.type == "code":
                current_part.content += "\n" + line
            elif line.startswith("|"):
                current_part = self.handle_table_line(line, current_part, parts)
            elif line.startswith("#"):
                current_part = self.handle_heading_line(line, current_part, parts)
            else:
                current_part = self.handle_text_line(line, current_part, parts)

        if current_part:
            parts.append(current_part)

        parts = self.filter_and_convert_tables(parts, node_id)
        parts = merge_consecutive_text_parts(parts)
        return parts

    def handle_code_block(
        self, line: str, current_part: Optional[Part], parts: List[Part]
    ) -> Optional[Part]:
        if current_part and current_part.type == "code":
            parts.append(current_part)
            current_part = None
            if len(line) > 3:
                parts.append(
                    Part(
                        id=f"id_{len(parts)}",
                        part_type="text",
                        content=line.lstrip("```"),
                    )
                )
        elif line.count("```") == 2 and line[-3] != "`":
            if current_part:
                parts.append(current_part)
            current_part = Part(
                id=f"id_{len(parts)}", part_type="code", content=line.lstrip("```")
            )
        elif current_part and current_part.type == "text":
            current_part.content += "\n" + line
        else:
            if current_part:
                parts.append(current_part)
            current_part = Part(id=f"id_{len(parts)}", part_type="text", content=line)
        return current_part

    def handle_table_line(
        self, line: str, current_part: Optional[Part], parts: List[Part]
    ) -> Optional[Part]:
        if current_part and current_part.type != "table":
            if current_part:
                parts.append(current_part)
            current_part = Part(id=f"id_{len(parts)}", part_type="table", content=line)
        elif current_part:
            current_part.content += "\n" + line
        else:
            current_part = Part(id=f"id_{len(parts)}", part_type="table", content=line)
        return current_part

    def handle_heading_line(
        self, line: str, current_part: Optional[Part], parts: List[Part]
    ) -> Optional[Part]:
        if current_part:
            parts.append(current_part)
        current_part = Part(
            id=f"id_{len(parts)}",
            part_type="title",
            content=line.lstrip("#"),
            title_level=len(line) - len(line.lstrip("#")),
        )
        return current_part

    def handle_text_line(
        self, line: str, current_part: Optional[Part], parts: List[Part]
    ) -> Optional[Part]:
        if current_part and current_part.type != "text":
            parts.append(current_part)
            current_part = Part(id=f"id_{len(parts)}", part_type="text", content=line)
        elif current_part:
            current_part.content += "\n" + line
        else:
            current_part = Part(id=f"id_{len(parts)}", part_type="text", content=line)
        return current_part

    def filter_and_convert_tables(
        self, parts: List[Part], node_id: Optional[str]
    ) -> List[Part]:
        for idx, part in enumerate(parts):
            if part.type == "table":
                should_keep, perfect_table = validate_table(part)
                if should_keep and perfect_table:
                    table = markdown_to_dataframe(part.content)
                    parts[idx] = create_table_part(part, table, node_id, None, idx)
                else:
                    parts[idx] = create_nonperfect_table_part(
                        part, node_id, None, idx, perfect_table
                    )
            else:
                parts[idx] = create_text_part(part, node_id, None, idx)
        return parts

    def get_table_elements(self, parts: List[Part]) -> List[Part]:
        return [e for e in parts if e.type == "table"]

    async def extract_table_summaries(self, parts: List[Part]) -> None:
        # Implementation for extracting table summaries asynchronously
        pass

    async def aextract_table_summaries(self, parts: List[Part]) -> None:
        # Implementation for extracting table summaries asynchronously
        pass

    def get_components_from_parts(
        self, parts: List[Part], node: Any, ref_doc_text: str
    ) -> List[Component]:
        components = []
        source_document = node.source_node or {"source": node.id_, "type": node.type}

        for part in parts:
            component = Component(id=part.id, content=part.content)
            component.relationships["source"] = source_document
            component.metadata.update(node.metadata)
            components.append(component)

        return components
