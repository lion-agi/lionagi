from typing import Any, Dict, Optional
import pandas as pd

md_json_char_map = {"'": '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}

py_json_msp = {
    "str": "string",
    "int": "number",
    "float": "number",
    "list": "array",
    "tuple": "array",
    "bool": "boolean",
    "dict": "object",
}


class Part:
    def __init__(
        self,
        id: str,
        part_type: str,
        content: Any,
        title_level: Optional[int] = None,
        table_output: Optional[Any] = None,
        table: Optional[pd.DataFrame] = None,
        markdown: Optional[str] = None,
        page_number: Optional[int] = None,
    ):
        self.id = id
        self.type = part_type
        self.content = content
        self.title_level = title_level
        self.table_output = table_output
        self.table = table
        self.markdown = markdown
        self.page_number = page_number
