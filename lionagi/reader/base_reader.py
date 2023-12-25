from pathlib import Path
from ..utils import dir_to_path

from typing import Callable, Dict, List, Optional, Union

def dir_to_files(dir: str, ext: str, recursive: bool = False,
                 reader: Callable = read_text, clean: bool = True,
                 to_csv: bool = False, project: str = 'project',
                 output_dir: str = 'data/logs/sources/', filename: Optional[str] = None,
                 verbose: bool = True, timestamp: bool = True, logger: Optional[DataLogger] = None):
    sources = dir_to_path(dir, ext, recursive)

    def _split_path(path: Path) -> tuple:
        folder_name = path.parent.name
        file_name = path.name
        return (folder_name, file_name)

    def _to_dict(path_: Path) -> Dict[str, Union[str, Path]]:
        folder, file = _split_path(path_)
        content = reader(str(path_), clean=clean)
        return {
            'project': project,
            'folder': folder,
            'file': file,
            "file_size": len(str(content)),
            'content': content
        } if content else None

    logs = to_list(l_call(sources, _to_dict, flat=True), dropna=True)

    if to_csv:
        filename = filename or f"{project}_sources.csv"
        logger = DataLogger(dir=output_dir, log=logs) if not logger else logger
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs