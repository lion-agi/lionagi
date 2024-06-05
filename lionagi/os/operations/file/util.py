import uuid
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd
from tqdm import tqdm

"""
the file management system is inspired/borrowed by llamaindex and langchain
both are MIT licensed
"""


# Constants
DEFAULT_SUMMARY_QUERY_STR = (
    "What is this table about? Give a very concise summary (imagine you are adding a new caption and summary for this table), "
    "and output the real/existing table title/caption if context provided. "
    "and output the real/existing table id if context provided. "
    "and also output whether or not the table should be kept."
)


# Models
class ColumnAnalysisResult:
    def __init__(self, col_name: str, col_type: str, summary: Optional[str] = None):
        self.col_name = col_name
        self.col_type = col_type
        self.summary = summary

    def __str__(self) -> str:
        return (
            f"Column: {self.col_name}\nType: {self.col_type}\nSummary: {self.summary}"
        )


class TableAnalysisResult:
    def __init__(
        self,
        summary: str,
        table_title: Optional[str] = None,
        table_id: Optional[str] = None,
        columns: List[ColumnAnalysisResult] = None,
    ):
        self.summary = summary
        self.table_title = table_title
        self.table_id = table_id
        self.columns = columns or []


class DocumentElement:
    def __init__(
        self,
        id: str,
        element_type: str,
        element: Any,
        title_level: Optional[int] = None,
        table_output: Optional[TableAnalysisResult] = None,
        table: Optional[pd.DataFrame] = None,
        markdown: Optional[str] = None,
        page_number: Optional[int] = None,
    ):
        self.id = id
        self.type = element_type
        self.element = element
        self.title_level = title_level
        self.table_output = table_output
        self.table = table
        self.markdown = markdown
        self.page_number = page_number
