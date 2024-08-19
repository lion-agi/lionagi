from typing import Any
import pandas as pd
from .convert import to_df


class PandasUtil:

    @staticmethod
    def to_df(
        input_: Any,
        /,
        *,
        drop_how: str = "all",
        drop_kwargs: dict[str, Any] | None = None,
        reset_index: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        return to_df(
            input_,
            drop_how=drop_how,
            drop_kwargs=drop_kwargs,
            reset_index=reset_index,
            **kwargs,
        )

    @staticmethod
    def extend_dataframe(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        /,
        unique_col: str = "node_id",
        keep="first",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Merges two DataFrames while ensuring no duplicate entries based on a specified unique column.

        Args:
            df1: The primary DataFrame.
            df2: The DataFrame to merge with the primary DataFrame.
            unique_col: The column name to check for duplicate entries. Defaults to 'node_id'.
            **kwargs: Additional keyword arguments for `drop_duplicates`.

        Returns:
            A DataFrame combined from df1 and df2 with duplicates removed based on the unique column.
        """
        try:
            if len(df2.dropna(how="all")) > 0 and len(df1.dropna(how="all")) > 0:
                df = to_df([df1, df2])
                df.drop_duplicates(
                    inplace=True, subset=[unique_col], keep=keep, **kwargs
                )
                df_ = to_df(df)
                if len(df_) > 1:
                    return df_
                else:
                    raise ValueError("No data to extend")

        except Exception as e:
            raise ValueError(f"Error in extending messages: {e}") from e

    @staticmethod
    def search_keywords(
        df: pd.DataFrame,
        /,
        keywords: str | list[str],
        *,
        column: str = "content",
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False,
    ) -> pd.DataFrame:
        """
        Filters a DataFrame for rows where a specified column contains given keywords.

        Args:
            df: The DataFrame to search through.
            keywords: A keyword or list of keywords to search for.
            col: The column to perform the search in. Defaults to "content".
            case_sensitive: Whether the search should be case-sensitive. Defaults to False.
            reset_index: Whether to reset the DataFrame's index after filtering. Defaults to False.
            dropna: Whether to drop rows with NA values before searching. Defaults to False.

        Returns:
            A filtered DataFrame containing only rows where the specified column contains
            any of the provided keywords.
        """

        if isinstance(keywords, list):
            keywords = "|".join(keywords)

        def handle_cases():
            if not case_sensitive:
                return df[df[column].str.contains(keywords, case=False)]
            else:
                return df[df[column].str.contains(keywords)]

        out = handle_cases()
        if reset_index or dropna:
            out = to_df(out, reset_index=reset_index)

        return out

    @staticmethod
    def replace_keyword(
        df: pd.DataFrame,
        /,
        keyword: str,
        replacement: str,
        *,
        inplace=True,
        column: str = "content",
        case_sensitive: bool = False,
    ) -> pd.DataFrame | bool:
        """
        Replaces occurrences of a specified keyword with a replacement string in a DataFrame column.

        Args:
            df: The DataFrame to modify.
            keyword: The keyword to be replaced.
            replacement: The string to replace the keyword with.
            col: The column in which to perform the replacement.
            case_sensitive: If True, performs a case-sensitive replacement. Defaults to False.
        """

        df_ = df.copy(deep=False) if inplace else df.copy()

        if not case_sensitive:
            df_.loc[:, column] = df_[column].str.replace(
                keyword, replacement, case=False, regex=False
            )
        else:
            df_.loc[:, column] = df_[column].str.replace(
                keyword, replacement, regex=False
            )

        return df_ if inplace else True

    @staticmethod
    def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
        """
        Reads a CSV file into a DataFrame with optional additional pandas read_csv parameters.

        Args:
            filepath: The path to the CSV file to read.
            **kwargs: Additional keyword arguments to pass to pandas.read_csv function.

        Returns:
            A DataFrame containing the data read from the CSV file.
        """
        df = pd.read_csv(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def read_json(filepath, **kwargs):
        df = pd.read_json(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def remove_last_n_rows(df: pd.DataFrame, steps: int) -> pd.DataFrame:
        """
        Removes the last 'n' rows from a DataFrame.

        Args:
            df: The DataFrame from which to remove rows.
            steps: The number of rows to remove from the end of the DataFrame.

        Returns:
            A DataFrame with the last 'n' rows removed.

        Raises:
            ValueError: If 'steps' is negative or greater than the number of rows in the DataFrame.
        """

        if steps < 0 or steps > len(df):
            raise ValueError(
                "'steps' must be a non-negative integer less than or equal to "
                "the length of DataFrame."
            )
        return to_df(df[:-steps])

    @staticmethod
    def update_row(
        df: pd.DataFrame, row: str | int, column: str | int, value: Any
    ) -> bool:
        """
        Updates a row's value for a specified column in a DataFrame.

        Args:
            df: The DataFrame to update.
            col: The column whose value is to be updated.
            old_value: The current value to search for in the specified column.
            new_value: The new value to replace the old value with.

        Returns:
            True if the update was successful, False otherwise.
        """

        try:
            df.loc[row, column] = value
            return True
        except Exception:
            return False

    # the following are borrowed from llama_index, MIT License
    # https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/node_parser/relational/utils.py

    @staticmethod
    def md_to_df(md_str: str) -> pd.DataFrame:
        from io import StringIO

        """Convert Markdown to dataframe."""
        # Replace " by "" in md_str
        md_str = md_str.replace('"', '""')

        # Replace markdown pipe tables with commas
        md_str = md_str.replace("|", '","')

        # Remove the second line (table header separator)
        lines = md_str.split("\n")
        md_str = "\n".join(lines[:1] + lines[2:])

        # Remove the first and last second char of the line (the pipes, transformed to ",")
        lines = md_str.split("\n")
        md_str = "\n".join([line[2:-2] for line in lines])

        # Check if the table is empty
        if len(md_str) == 0:
            return None

        # Use pandas to read the CSV string into a DataFrame
        return pd.read_csv(StringIO(md_str))

    @staticmethod
    def html_to_df(html_str: str) -> pd.DataFrame:
        """Convert HTML to dataframe."""
        try:
            from lionagi.os.sys_util import SysUtil

            html = SysUtil.check_import(
                package_name="lxml",
                import_name="html",
            )
        except ImportError:
            raise ImportError(
                "You must install the `lxml` package to use this node parser."
            )

        tree = html.fromstring(html_str)
        table_element = tree.xpath("//table")[0]
        rows = table_element.xpath(".//tr")

        data = []
        for row in rows:
            cols = row.xpath(".//td")
            cols = [c.text.strip() if c.text is not None else "" for c in cols]
            data.append(cols)

        # Check if the table is empty
        if len(data) == 0:
            return None

        # Check if the all rows have the same number of columns
        if not all(len(row) == len(data[0]) for row in data):
            return None

        return pd.DataFrame(data[1:], columns=data[0])

    @staticmethod
    def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
        """
        Reads a CSV file into a DataFrame with optional additional pandas read_csv parameters.

        Args:
            filepath: The path to the CSV file to read.
            **kwargs: Additional keyword arguments to pass to pandas.read_csv function.

        Returns:
            A DataFrame containing the data read from the CSV file.
        """
        df = pd.read_csv(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def read_json(filepath, **kwargs):
        df = pd.read_json(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def remove_last_n_rows(df: pd.DataFrame, steps: int) -> pd.DataFrame:
        """
        Removes the last 'n' rows from a DataFrame.

        Args:
            df: The DataFrame from which to remove rows.
            steps: The number of rows to remove from the end of the DataFrame.

        Returns:
            A DataFrame with the last 'n' rows removed.

        Raises:
            ValueError: If 'steps' is negative or greater than the number of rows in the DataFrame.
        """

        if steps < 0 or steps > len(df):
            raise ValueError(
                "'steps' must be a non-negative integer less than or equal to "
                "the length of DataFrame."
            )
        return to_df(df[:-steps])
