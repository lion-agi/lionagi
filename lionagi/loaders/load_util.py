# use utils and schema
import math
from enum import Enum
from pathlib import Path
from typing import List, Union, Dict, Any, Tuple

from ..utils import to_list, lcall
from ..schema import DataNode

class ReaderType(str, Enum):
    PLAIN = 'plain'
    LANGCHAIN = 'langchain'
    LLAMAINDEX = 'llama_index'
    SELFDEFINED = 'self_defined'


class ChunkerType(str, Enum):
    PLAIN = 'plain'                 # default
    LANGCHAIN = 'langchain'         # using langchain functions
    LLAMAINDEX = 'llama_index'      # using llamaindex functions
    SELFDEFINED = 'self_defined'    # create custom functions
    
    
def dir_to_path(
    dir: str, ext: str, recursive: bool = False, 
    flatten: bool = True
) -> List[Path]:
    """
    Generates a list of file paths from a directory with the given file extension.

    Parameters:
        dir (str): The directory to search for files.

        ext (str): The file extension to filter by.

        recursive (bool): Whether to search subdirectories recursively. Defaults to False.

        flatten (bool): Whether to flatten the list. Defaults to True.
    
    Returns:
        List[Path]: A list of Paths to the files.

    Raises:
        ValueError: If the directory or extension is invalid.
    """
    
    def _dir_to_path(ext):
        tem = '**/*' if recursive else '*'
        return list(Path(dir).glob(tem + ext))
    
    try: 
        return to_list(lcall(ext, _dir_to_path, flatten=True), flatten=flatten)
    except: 
        raise ValueError("Invalid directory or extension, please check the path")

def dir_to_nodes(
    dir: str, ext: Union[List[str], str], 
    recursive: bool = False, flatten: bool = True, 
    clean_text: bool = True
) -> List[DataNode]:
    """
    Converts directory contents into DataNode objects based on specified file extensions.

    This function first retrieves a list of file paths from the specified directory, matching the given file extension. It then reads the content of these files, optionally cleaning the text, and converts each file's content into a DataNode object. 

    Parameters:
        dir (str): The directory path from which to read files.
        ext: The file extension(s) to include. Can be a single string or a list/tuple of strings.
        recursive (bool, optional): If True, the function searches for files recursively in subdirectories. Defaults to False.
        flatten (bool, optional): If True, flattens the directory structure in the returned paths. Defaults to True.
        clean_text (bool, optional): If True, cleans the text read from files. Defaults to True.

    Returns:
        list: A list of DataNode objects created from the files in the specified directory.

    Example:
        nodes = dir_to_nodes("/path/to/dir", ".txt", recursive=True)
        # This would read all .txt files in /path/to/dir and its subdirectories, 
        # converting them into DataNode objects.
    """

    path_list = dir_to_path(dir, ext, recursive, flatten)
    files_info = lcall(path_list, read_text, clean=clean_text)
    nodes = lcall(files_info, lambda x: DataNode(content=x[0], metadata=x[1]))
    return nodes

def chunk_text(input: str, 
               chunk_size: int, 
               overlap: float,
               threshold: int) -> List[Union[str, None]]:
    """
    Chunks the input text into smaller parts, with optional overlap and threshold for final chunk.

    Parameters:
        input (str): The input text to chunk.

        chunk_size (int): The size of each chunk.

        overlap (float): The amount of overlap between chunks.

        threshold (int): The minimum size of the final chunk.

    Returns:
        List[Union[str, None]]: A list of text chunks.

    Raises:
        ValueError: If an error occurs during chunking.
    """
    
    def _chunk_n1():
        return [input]
        
    def _chunk_n2():
        chunks = []
        chunks.append(input[:chunk_size + overlap_size])
        
        if len(input) - chunk_size > threshold:
            chunks.append(input[chunk_size - overlap_size:])    
        else:
            return _chunk_n1()
        
        return chunks

    def _chunk_n3():
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
    
    try:
        if not isinstance(input, str): input = str(input)
        
        n_chunks = math.ceil(len(input) / chunk_size)
        overlap_size = int(overlap / 2)

        if n_chunks == 1: 
            return _chunk_n1()
        
        elif n_chunks == 2:
            return _chunk_n2()
        
        elif n_chunks > 2:
            return _chunk_n3()

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")

def read_text(filepath: str, clean: bool = True) -> Tuple[str, dict]:
    """
    Reads text from a file and optionally cleans it, returning the content and metadata.

    Parameters:
        filepath (str): The path to the file to read.

        clean (bool): Whether to clean the text by replacing certain characters. Defaults to True.

    Returns:
        Tuple[str, dict]: A tuple containing the content and metadata of the file.

    Raises:
        FileNotFoundError: If the file cannot be found.

        PermissionError: If there are permissions issues.

        OSError: For other OS-related errors.
    """
    def _get_metadata():
        import os
        from datetime import datetime
        file = filepath
        size = os.path.getsize(filepath)
        creation_date = datetime.fromtimestamp(os.path.getctime(filepath)).date()
        modified_date = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
        last_accessed_date = datetime.fromtimestamp(os.path.getatime(filepath)).date()
        return {'file': str(file),
                'size': size,
                'creation_date': str(creation_date),
                'modified_date': str(modified_date),
                'last_accessed_date': str(last_accessed_date)}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if clean:
                # Define characters to replace and their replacements
                replacements = {'\\': ' ', '\n': ' ', '\t': ' ', '  ': ' ', '\'': ' '}
                for old, new in replacements.items():
                    content = content.replace(old, new)
            metadata = _get_metadata()
            return content, metadata
    except Exception as e:
        raise e
    
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


# needs doing TODO
def file_to_chunks(input,
                #    project='project',
                #    output_dir='data/logs/sources/',
                   chunk_func = _file_to_chunks,  **kwargs):
                #    out_to_csv=False,
                #    filename=None,
                #    verbose=True,
                #    timestamp=True,
                #    logger=None,
    logs = to_list(lcall(input, chunk_func, **kwargs), flatten=True)
    return logs
