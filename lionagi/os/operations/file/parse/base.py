from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from ..util import DocumentElement, TableAnalysisResult, DEFAULT_SUMMARY_QUERY_STR
import pandas as pd
import uuid
from tqdm import tqdm
from typing import Any, List, Optional, Dict, Sequence, Tuple


class Parser:
    def __init__(
        self,
        llm: Optional[Any] = None,
        summary_query_str: str = DEFAULT_SUMMARY_QUERY_STR,
        num_workers: int = 4,
        show_progress: bool = True,
        nested_node_parser: Optional[Any] = None,
    ):
        self.llm = llm
        self.summary_query_str = summary_query_str
        self.num_workers = num_workers
        self.show_progress = show_progress
        self.nested_node_parser = nested_node_parser

    @abstractmethod
    def extract_elements(self, text: str, **kwargs: Any) -> List[DocumentElement]:
        pass

    def get_table_elements(
        self, elements: List[DocumentElement]
    ) -> List[DocumentElement]:
        return [e for e in elements if e.type in ["table", "table_text"]]

    def get_text_elements(
        self, elements: List[DocumentElement]
    ) -> List[DocumentElement]:
        return [e for e in elements if e.type != "table"]

    async def extract_table_summaries(self, elements: List[DocumentElement]) -> None:
        table_context_list = self._prepare_table_contexts(elements)
        summary_jobs = [
            self._get_table_output(ctx, self.summary_query_str)
            for ctx in table_context_list
        ]
        summary_outputs = await self._run_jobs(
            summary_jobs, self.show_progress, self.num_workers
        )

        for element, summary_output in zip(elements, summary_outputs):
            element.table_output = summary_output

    def _prepare_table_contexts(self, elements: List[DocumentElement]) -> List[str]:
        table_context_list = []
        for idx, element in tqdm(enumerate(elements)):
            if element.type not in ["table", "table_text"]:
                continue
            context = str(element.element)
            if idx > 0 and elements[idx - 1].element.lower().strip().startswith(
                "table"
            ):
                context = str(elements[idx - 1].element) + "\n" + context
            if idx < len(elements) - 1 and elements[
                idx + 1
            ].element.lower().strip().startswith("table"):
                context += "\n" + str(elements[idx + 1].element)
            table_context_list.append(context)
        return table_context_list

    async def _get_table_output(
        self, table_context: str, summary_query_str: str
    ) -> Any:
        response = await self.llm.aquery(table_context, query=summary_query_str)
        return TableAnalysisResult(summary=response)

    def convert_table_to_markdown(self, element: DocumentElement) -> str:
        if element.type == "table":
            return self._table_to_markdown(element.table)
        return str(element.element)

    def _table_to_markdown(self, table: pd.DataFrame) -> str:
        table_md = (
            "|"
            + "|".join(table.columns)
            + "|\n|"
            + "|".join("---" for _ in table.columns)
            + "|\n"
        )
        for row in table.itertuples(index=False):
            table_md += "|" + "|".join(str(cell) for cell in row) + "|\n"
        return table_md

    def get_table_char_indices(
        self, element: DocumentElement, ref_doc_text: Optional[str]
    ) -> Tuple[Optional[int], Optional[int]]:
        if ref_doc_text:
            start_char_idx = ref_doc_text.find(str(element.element))
            end_char_idx = (
                start_char_idx + len(str(element.element))
                if start_char_idx >= 0
                else None
            )
            return start_char_idx, end_char_idx
        return None, None

    async def parse_nodes(
        self, nodes: Sequence[Any], show_progress: bool = False, **kwargs: Any
    ) -> List[Any]:
        all_nodes = []
        nodes_with_progress = self._get_tqdm_iterable(
            nodes, show_progress, "Parsing nodes"
        )
        for node in nodes_with_progress:
            parsed_nodes = await self.get_nodes_from_node(node)
            all_nodes.extend(parsed_nodes)
        return all_nodes

    @abstractmethod
    async def get_nodes_from_node(self, node: Any) -> List[Any]:
        pass

    def get_nodes_from_elements(
        self,
        elements: List[DocumentElement],
        inherited_node: Optional[Any] = None,
        ref_doc_text: Optional[str] = None,
    ) -> List[Any]:
        nodes = []
        text_buffer = []

        for element in elements:
            if element.type in ["table", "table_text"]:
                if text_buffer:
                    nodes.extend(self._create_text_nodes_from_buffer(text_buffer))
                    text_buffer = []
                nodes.extend(self._create_table_nodes(element, ref_doc_text))
            else:
                text_buffer.append(str(element.element))

        if text_buffer:
            nodes.extend(self._create_text_nodes_from_buffer(text_buffer))

        return nodes

    def _create_text_nodes_from_buffer(self, buffer: List[str]) -> List[Any]:
        document_text = "\n\n".join(buffer)
        document = {"text": document_text}
        return self.get_nodes_from_documents([document])

    def _create_table_nodes(
        self, element: DocumentElement, ref_doc_text: Optional[str]
    ) -> List[Any]:
        table_output = element.table_output
        markdown_table = self.convert_table_to_markdown(element)
        column_schema = "\n\n".join(str(col) for col in table_output.columns)

        summary_text = self._compose_table_summary(table_output)
        start_idx, end_idx = self._determine_char_indices(element, ref_doc_text)
        node_id = str(uuid.uuid4())

        node = self._create_node(
            summary_text, column_schema, markdown_table, node_id, start_idx, end_idx
        )
        return [node]

    def _compose_table_summary(self, table_output: TableAnalysisResult) -> str:
        summary = table_output.summary
        if table_output.table_title:
            summary += f",\nwith the following table title:\n{table_output.table_title}"
        summary += ",\nwith the following columns:\n" + "\n".join(
            f"- {col.col_name}: {col.summary}" for col in table_output.columns
        )
        return summary

    def _determine_char_indices(
        self, element: DocumentElement, ref_doc_text: Optional[str]
    ) -> Tuple[Optional[int], Optional[int]]:
        if ref_doc_text:
            start_idx = ref_doc_text.find(str(element.element))
            end_idx = start_idx + len(str(element.element)) if start_idx >= 0 else None
            return start_idx, end_idx
        return None, None

    def _create_node(
        self,
        summary: str,
        schema: str,
        markdown_table: str,
        node_id: str,
        start_idx: Optional[int],
        end_idx: Optional[int],
    ) -> Any:
        combined_text = f"{summary}\n{markdown_table}"
        return {
            "id_": node_id,
            "text": combined_text,
            "metadata": {
                "table_df": markdown_table,
                "table_summary": summary,
                "col_schema": schema,
            },
            "excluded_embed_metadata_keys": ["table_df", "table_summary", "col_schema"],
            "excluded_llm_metadata_keys": ["table_df", "table_summary", "col_schema"],
            "start_char_idx": start_idx,
            "end_char_idx": end_idx,
        }

    def _get_nodes_from_buffer(self, buffer: List[str]) -> List[Any]:
        doc = {"text": "\n\n".join(buffer)}
        return self.get_nodes_from_documents([doc])

    @abstractmethod
    def get_nodes_from_documents(self, docs: List[Any], **kwargs: Any) -> List[Any]:
        pass

    def _get_tqdm_iterable(
        self, iterable: Sequence[Any], show_progress: bool, desc: str
    ) -> Sequence[Any]:
        return tqdm(iterable, desc=desc) if show_progress else iterable

    def __call__(self, nodes: List[Any], **kwargs: Any) -> List[Any]:
        return self.get_nodes_from_documents(nodes, **kwargs)

    async def acall(self, nodes: List[Any], **kwargs: Any) -> List[Any]:
        return await self.aget_nodes_from_documents(nodes, **kwargs)
