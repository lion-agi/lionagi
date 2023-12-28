import math
from pathlib import Path
from typing import Any, Dict, List, Union, Callable, Optional

from ..utils.sys_utils import to_list, l_call
from ..schema import DataLogger

def _dir_to_path(dir, ext, recursive):
    tem = '**/*' if recursive else '*'
    return list(Path(dir).glob(tem + ext))

def _split_path(path: Path) -> tuple:
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def dir_to_path(dir: str, ext, recursive: bool = False, flat: bool = True):
    try: 
        return to_list(l_call(ext, _dir_to_path, flat=True, 
                              recursive=recursive, dir=dir, ext=ext), 
                       flat=flat)
    except: 
        raise ValueError("Invalid directory or extension, please check the path")
    
def read_text(filepath: str, clean: bool = True) -> str:
    with open(filepath, 'r') as f:
        content = f.read()
        if clean:
            # Define characters to replace and their replacements
            replacements = {'\\': ' ', '\n': ' ', '\t': ' ', '  ': ' ', '\'': ' '}
            for old, new in replacements.items():
                content = content.replace(old, new)
        return content

def dir_to_files(dir: str, 
                 ext: str, 
                 recursive: bool = False,
                 reader: Callable = read_text, 
                 clean: bool = True,
                 to_csv: bool = False, 
                 project: str = 'project',
                 output_dir: str = 'data/logs/sources/', 
                 filename: Optional[str] = None,
                 verbose: bool = True, 
                 timestamp: bool = True, 
                 logger: Optional[DataLogger] = None):

    sources = dir_to_path(dir, ext, recursive)

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

def _chunk_n1(input):
    return [input]
    
def _chunk_n2(input, chunk_size, overlap_size, threshold):
    chunks = []
    chunks.append(input[:chunk_size + overlap_size])
    if len(input) - chunk_size > threshold:
        chunks.append(input[chunk_size - overlap_size:])
    else:
        return [input]
    return chunks

def _chunk_n3(input, chunk_size, overlap_size, threshold, n_chunks):
    chunks = []
    chunks.append(input[:chunk_size + overlap_size])
    for i in range(1, n_chunks - 1):
        start_idx = chunk_size * i - overlap_size
        end_idx = chunk_size * (i + 1) + overlap_size
        chunks.append(input[start_idx:end_idx])

    if len(input) - chunk_size * (n_chunks - 1) > threshold:
        chunks.append(input[chunk_size * (n_chunks - 1) - overlap_size:])
    else:
        chunks[-1] += input[chunk_size * (n_chunks - 1) + overlap_size:]

    return chunks

def chunk_text(input: str, 
               chunk_size: int, 
               overlap: float,
               threshold: int) -> List[Union[str, None]]:
    try:
        if not isinstance(input, str): input = str(input)
        
        n_chunks = math.ceil(len(input) / chunk_size)
        overlap_size = int(chunk_size * overlap / 2)

        if n_chunks == 1: return _chunk_n1(input)
        
        elif n_chunks == 2:
            return _chunk_n2(input=input, chunk_size=chunk_size, overlap_size=overlap_size, 
                             threshold=threshold)
        elif n_chunks > 2:
            return _chunk_n3(input=input, chunk_size=chunk_size, overlap_size=overlap_size, 
                             threshold=threshold, n_chunks=n_chunks)

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")

def _file_to_chunks(input: Dict[str, Any],
                   field: str = 'content',
                   chunk_size: int = 1500,
                   overlap: float = 0.1,
                   threshold: int = 200) -> List[Dict[str, Any]]:
    try:
        out = {key: value for key, value in input.items() if key != field}
        out.update({"chunk_overlap": overlap, "chunk_threshold": threshold})

        chunks = chunk_text(input[field], chunk_size=chunk_size, overlap=overlap, threshold=threshold)
        logs = []
        for i, chunk in enumerate(chunks):
            chunk_dict = out.copy()
            chunk_dict.update({
                'file_chunks': len(chunks),
                'chunk_id': i + 1,
                'chunk_size': len(chunk),
                f'chunk_{field}': chunk
            })
            logs.append(chunk_dict)

        return logs

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the file. {e}")

def file_to_chunks(input,
                   project='project',
                   output_dir='data/logs/sources/',
                   chunk_func = _file_to_chunks,
                   to_csv=False,
                   filename=None,
                   verbose=True,
                   timestamp=True,
                   logger=None, **kwargs):
    logs = to_list(l_call(input, chunk_func, **kwargs), flat=True)

    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logger = logger or DataLogger(log=logs)
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs
