from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from .util import Part


# needs doing
def filter_table_part(table_df):
    return table_df is not None and not table_df.empty and len(table_df.columns) > 1


def create_part(
    part_type: str, element_idx: int, page_number: int, json_item: Dict[str, Any]
) -> Part:
    return Part(
        id=f"id_page_{page_number}_{part_type}_{element_idx}",
        part_type=part_type,
        title_level=json_item.get("lvl"),
        content=json_item.get("value"),
        markdown=json_item.get("md"),
        page_number=page_number,
    )


def validate_table(part: Part) -> Tuple[bool, bool]:
    should_keep = True
    perfect_table = True

    table_lines = part.markdown.split("\n")
    table_columns = [len(line.split("|")) for line in table_lines]
    if len(set(table_columns)) > 1:
        perfect_table = False

    if len(table_lines) < 2:
        should_keep = False

    return should_keep, perfect_table


def create_table_part(
    part: Part,
    table: pd.DataFrame,
    node_id: Optional[str],
    page_number: Optional[int],
    idx: int,
) -> Part:
    return Part(
        id=(f"id_page_{page_number}_{node_id}_{idx}" if node_id else f"id_{idx}"),
        part_type="table",
        content=part.content,
        table=table,
    )


def create_nonperfect_table_part(
    part: Part,
    node_id: Optional[str],
    page_number: Optional[int],
    idx: int,
    perfect_table: bool,
) -> Part:
    return Part(
        id=(f"id_page_{page_number}_{node_id}_{idx}" if node_id else f"id_{idx}"),
        part_type="table_text" if not perfect_table else "text",
        content=part.content,
    )


def create_text_part(
    part: Part, node_id: Optional[str], page_number: Optional[int], idx: int
) -> Part:
    return Part(
        id=(
            f"id_page_{page_number}_{node_id}_{idx}"
            if node_id
            else f"id_page_{page_number}_{idx}"
        ),
        part_type="text",
        content=part.content,
    )


def merge_consecutive_text_parts(parts: List[Part]) -> List[Part]:
    merged_parts = []
    for part in parts:
        if merged_parts and part.type == "text" and merged_parts[-1].type == "text":
            merged_parts[-1].content += "\n" + part.content
        else:
            merged_parts.append(part)
    return merged_parts


def markdown_to_dataframe(md: str) -> pd.DataFrame:
    return pd.read_csv(pd.compat.StringIO(md), sep="|", engine="python")
