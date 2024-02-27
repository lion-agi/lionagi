import logging
import re
from pathlib import Path
from shutil import copy2
import logging
import re
from pathlib import Path


class PathUtil:

    @staticmethod
    def clear_dir(
        dir_path: Path | str, recursive: bool = False, exclude: list[str] = None
    ) -> None:
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(
                f"The specified directory {dir_path} does not exist."
            )

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in dir_path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            if recursive and file_path.is_dir():
                PathUtil.clear_dir(file_path, recursive=True, exclude=exclude)
            elif file_path.is_file() or file_path.is_symlink():
                try:
                    file_path.unlink()
                    logging.info(f"Successfully deleted {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {file_path}. Reason: {e}")
                    raise

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def create_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        custom_timestamp_format: str | None = None,
    ) -> Path:
        directory = Path(directory)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError(
                "Invalid filename. Ensure it doesn't contain illegal characters and has a valid extension."
            )

        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        ext = f".{ext}" if ext else ""

        timestamp_str = ""
        if timestamp:
            from datetime import datetime

            timestamp_format = custom_timestamp_format or "%Y%m%d%H%M%S"
            timestamp_str = datetime.now().strftime(timestamp_format)
            filename = (
                f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
            )
        else:
            filename = name

        full_filename = f"{filename}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    def list_files(dir_path: Path | str, extension: str = None) -> list[Path]:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")
        if extension:
            return list(dir_path.glob(f"*.{extension}"))
        else:
            return list(dir_path.glob("*"))

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str) -> None:
        src, dest = Path(src), Path(dest)
        if not src.is_file():
            raise FileNotFoundError(f"{src} does not exist or is not a file.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(src, dest)

    @staticmethod
    def get_size(path: Path | str) -> int:
        path = Path(path)
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
        else:
            raise FileNotFoundError(f"{path} does not exist.")
