from pathlib import Path

from lionagi.utils import create_path

from .process import dir_to_files


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
) -> list[str] | str | tuple[list[str], list[Path]] | tuple[str, list[Path]]:
    """
    data_path: str or Path or list of str or Path, the directory or file paths to concatenate.
    file_types: list of str, the file types to concatenate. [e.g. ['.txt', '.md']]
    output_dir: str or Path, the directory to save the concatenated file. If provided, will save the file.
    output_filename: str, the filename to save the concatenated file.
    file_exist_ok: bool, if True, overwrite the existing file. Default is True.
    recursive: bool, if True, search files recursively. Default is True.
    verbose: bool, if True, print the output path. Default is True.
    threshold: int, the minimum number of chars for the file to be considered valid to concatenate.
    kwargs: additional keyword arguments to pass to create_path.
    """
    persist_path = None
    if output_dir:
        if not output_filename:
            output_filename = "concatenated_text.txt"
            kwargs["timestamp"] = kwargs.get("timestamp", True)
            kwargs["random_hash_digits"] = kwargs.get("random_hash_digits", 6)
        output_filename = output_filename or "concatenated_text.txt"
        persist_path = create_path(
            output_dir, output_filename, file_exist_ok=file_exist_ok, **kwargs
        )

    texts = []
    data_path = (
        [str(data_path)] if not isinstance(data_path, list) else data_path
    )
    data_path = sorted(data_path)
    data_path = [Path(dp) for dp in data_path if Path(dp).exists()]

    for dp in data_path:
        fps = dir_to_files(dp, recursive=recursive, file_types=file_types)

        data_path = sorted([str(i) for i in fps])
        data_path: list[Path] = [
            Path(dp) for dp in data_path if Path(dp).exists()
        ]

        for fp in data_path:
            text = fp.read_text(encoding="utf-8")
            if len(text) >= threshold:
                fp_text = (
                    "\n----------------------------------------------------\n"
                    f"{str(fp)}"
                    "\n----------------------------------------------------\n"
                )
                text = fp_text + text
                texts.append(text)

    text = "\n".join(texts)
    if persist_path:
        persist_path.write_text(text, encoding="utf-8")
    if verbose:
        print(f"Concatenated {len(fps)} files to {persist_path}")
        print(f"The file contains {len(text)} characters.")

    if return_files:
        if return_fps:
            return texts, fps
        return texts

    if return_fps:
        return text, fps
    return text
