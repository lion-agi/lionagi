from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from lionagi.protocols._concepts import Manager

if TYPE_CHECKING:
    from lionagi.protocols.graph.node import Node


class FileManager(Manager):

    @staticmethod
    def dir_to_files(
        directory: str | Path,
        file_types: list[str] | None = None,
        max_workers: int | None = None,
        ignore_errors: bool = False,
        verbose: bool = False,
        recursive: bool = False,
    ) -> list[Path]:
        """
        Recursively process a directory and return a list of file paths.

        This function walks through the given directory and its subdirectories,
        collecting file paths that match the specified file types (if any).

        directory: str or Path, the directory to process.
        file_types: list of str, optional, the file types to include. If None, all files are included.
        max_workers: int, optional, the maximum number of threads to use for processing.
        ignore_errors: bool, optional, if True, errors during file processing are ignored.
        verbose: bool, optional, if True, prints the number of files processed.
        recursive: bool, optional, if True, processes files in subdirectories as well.
        """
        from .process import dir_to_files

        return dir_to_files(**locals())

    @staticmethod
    def concat_files(
        data_path: str | Path | list,
        file_types: list[str],
        output_dir: str | Path = None,
        output_filename: str = None,
        file_exist_ok: bool = True,
        recursive: bool = True,
        verbose: bool = True,
        threshold: int = 0,
        return_fps: bool = False,
        return_files: bool = False,
        **kwargs,
    ) -> (
        list[str] | str | tuple[list[str], list[Path]] | tuple[str, list[Path]]
    ):
        from .concat_files import concat_files

        params = {k: v for k, v in locals().items() if k != "kwargs"}
        params.update(kwargs)
        return concat_files(**params)

    @staticmethod
    def chunk(
        *,
        text: str | None = None,
        url_or_path: str | Path = None,
        file_types: list[str] | None = None,  # only local files
        recursive: bool = False,  # only local files
        tokenizer: Callable[[str], list[str]] = None,
        chunk_by: Literal["chars", "tokens"] = "chars",
        chunk_size: int = 2048,
        overlap: float = 0,
        threshold: int = 0,
        output_file: str | Path | None = None,
        metadata: dict[str, Any] | None = None,
        reader_tool: Callable = None,
        as_node: bool = False,
    ) -> list[Node | dict]:
        from .process import chunk

        return chunk(**locals())

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str) -> None:
        from .file_ops import copy_file
        copy_file(src, dest)

    @staticmethod
    def read_file(path: Path | str) -> str: ...
