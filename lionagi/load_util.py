from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Union
from .schema import Chunk, DataLogger
from .utils import l_call, to_list
from .loader.reader import read_text
from .loader.chunker import chunk_text

def split_path(path: Path) -> tuple:
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)
    

def dir_to_path(dir: str, ext, recursive: bool = False, flat: bool = True):

    def _dir_to_path(ext, recursive=recursive):
        tem = '**/*' if recursive else '*'
        return list(Path(dir).glob(tem + ext))

    try: 
        return to_list(l_call(ext, _dir_to_path, flat=True), flat=flat)
    except: 
        raise ValueError("Invalid directory or extension, please check the path")


def dir_to_files(dir: str, ext: str, recursive: bool = False,
                 reader: Callable = read_text, clean: bool = True,
                 to_csv: bool = False, project: str = 'project',
                 output_dir: str = 'data/logs/sources/', filename: Optional[str] = None,
                 verbose: bool = True, timestamp: bool = True, logger: Optional[DataLogger] = None):
    sources = dir_to_path(dir, ext, recursive)


    def _to_dict(path_: Path) -> Dict[str, Union[str, Path]]:
        folder, file = split_path(path_)
        content = reader(str(path_), clean=clean)
        file_ = File()
        
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

def _file_to_chunks(file_, chunker=None, **kwags):
    if not chunker: 
        try:
            from llama_index.text_splitter import SentenceSplitter
            chunker = SentenceSplitter
        except Exception as e:
            raise ImportError(f"An error occurred while importing the chunker. {e}")
    try:
        nodes = chunker.get_nodes_from_documents(file_.to_llama(), **kwags)
        chunks = l_call(nodes, Chunk().from_llama(nodes))
        return chunks
    except Exception as e:
        raise ValueError(f"An error occurred while chunking the file. {e}")

def files_to_chunks(file_, chunker=None, verbose=True, 
                   filename=None, timestamp=True, to_csv=False, 
                   output_dir='data/logs/sources/', project=None, **kwags):
    
    _f = lambda x: _file_to_chunks(x, chunker ,**kwags)
    chunks = to_list(l_call(file_, _f))
    
    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logs = l_call(chunks, lambda x: x.to_json())
        logger = DataLogger(log=logs) if not logger else logger
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return chunks