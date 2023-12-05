import math
from pathlib import Path
from typing import Any, Dict, List, Union, Callable, Optional

from .sys_util import to_list, l_call
from .log_util import DataLogger


def dir_to_path(dir: str, ext, recursive: bool = False, flat: bool = True):
    """
    Retrieves a list of file paths in the specified directory with the given extension.

    Parameters:
        dir (str): The directory path where to search for files.
        ext (str): The file extension to filter by.
        recursive (bool, optional): If True, search for files recursively in subdirectories. Defaults to False.
        flat (bool, optional): If True, return a flat list of file paths. Defaults to True.

    Returns:
        List[str]: A list of file paths that match the given extension within the specified directory.

    Example:
        >>> files = dir_to_path(dir='my_directory', ext='.txt', recursive=True, flat=True)
    """

    def _dir_to_path(ext, recursive=recursive):
        tem = '**/*' if recursive else '*'
        return list(Path(dir).glob(tem + ext))
    
    return to_list(l_call(ext, _dir_to_path, flat=True), flat=flat)

def read_text(filepath: str, clean: bool = True) -> str:
    """
    Reads the content of a text file and optionally cleans it by removing specified characters.

    Parameters:
        filepath (str): The path to the text file to be read.
        clean (bool, optional): If True, clean the content by removing specific unwanted characters. Defaults to True.

    Returns:
        str: The cleaned (if 'clean' is True) or raw content of the text file.

    Example:
        >>> content = read_text(filepath='example.txt', clean=True)
    """

    with open(filepath, 'r') as f:
        content = f.read()
        if clean:
            # Define characters to replace and their replacements
            replacements = {'\\': ' ', '\\\n': ' ', '\\\t': ' ', '  ': ' ', '\'': ' '}
            for old, new in replacements.items():
                content = content.replace(old, new)
        return content

def dir_to_files(dir: str, ext: str, recursive: bool = False, 
                 reader: Callable = read_text, clean: bool = True, 
                 to_csv: bool = False, project: str = 'project',
                 output_dir: str = 'data/logs/sources/', filename: Optional[str] = None, 
                 verbose: bool = True, timestamp: bool = True, logger: Optional[DataLogger] = None):
    """
    Reads and processes files in a specified directory with the given extension.

    Parameters:
        dir (str): The directory path where files are located.
        ext (str): The file extension to filter by.
        recursive (bool, optional): If True, search files recursively in subdirectories. Defaults to False.
        reader (Callable, optional): Function used to read and process the content of each file. Defaults to read_text.
        clean (bool, optional): If True, cleans the content by removing specified characters. Defaults to True.
        to_csv (bool, optional): If True, export the processed data to a CSV file. Defaults to False.
        project (str, optional): The name of the project. Defaults to 'project'.
        output_dir (str, optional): Directory path for exporting the CSV file. Defaults to 'data/logs/sources/'.
        filename (Optional[str], optional): Name of the CSV file, if not provided, a default will be used. Defaults to None.
        verbose (bool, optional): If True, print a message upon CSV export. Defaults to True.
        timestamp (bool, optional): If True, include a timestamp in the file name. Defaults to True.
        logger (Optional[DataLogger], optional): An instance of DataLogger for logging, if not provided, a new one will be created. Defaults to None.

    Returns:
        List[Dict[str, Union[str, Path]]]: A list of dictionaries containing file information and content.

    Examples:
        >>> logs = dir_to_files(dir='my_directory', ext='.txt', to_csv=True)
    """
    
    sources = dir_to_path(dir, ext, recursive)
    
    def split_path(path: Path) -> tuple:
        folder_name = path.parent.name
        file_name = path.name
        return (folder_name, file_name)

    def to_dict(path_: Path) -> Dict[str, Union[str, Path]]:
        folder, file = split_path(path_)
        content = reader(str(path_), clean=clean)
        return {
            'project': project,
            'folder': folder,
            'file': file,
            "file_size": len(str(content)),
            'content': content
        } if content else None
    
    logs = to_list(l_call(sources, to_dict, flat=True), dropna=True)
    
    if to_csv:
        filename = filename or f"{project}_sources.csv"
        logger = DataLogger(dir=output_dir, log=logs) if not logger else logger
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs

def chunk_text(input: str, chunk_size: int, overlap: float, 
               threshold: int) -> List[Union[str, None]]:
    """
    Splits a string into chunks of a specified size, allowing for optional overlap between chunks.
    
    Args:
        input (str): The text to be split into chunks.
        chunk_size (int): The size of each chunk in characters.
        overlap (float): A value between [0, 1] specifying the percentage of overlap between adjacent chunks.
        threshold (int): The minimum size for the last chunk. If the last chunk is smaller than this, it will be merged with the previous chunk.
        
    Raises:
        TypeError: If input text cannot be converted to a string.
        ValueError: If any error occurs during the chunking process.
        
    Returns:
        List[Union[str, None]]: List of text chunks.
    """
    
    try:
        # Ensure text is a string
        if not isinstance(input, str):
            input = str(input)
        
        chunks = []
        n_chunks = math.ceil(len(input) / chunk_size)
        overlap_size = int(chunk_size * overlap / 2)
        
        if n_chunks == 1:
            return [input]
        
        elif n_chunks == 2:
            chunks.append(input[:chunk_size + overlap_size])
            if len(input) - chunk_size > threshold:
                chunks.append(input[chunk_size - overlap_size:])
            else:
                return [input]
            return chunks
        
        elif n_chunks > 2:
            chunks.append(input[:chunk_size + overlap_size])
            for i in range(1, n_chunks - 1):
                start_idx = chunk_size * i - overlap_size
                end_idx = chunk_size * (i + 1) + overlap_size
                chunks.append(input[start_idx:end_idx])
            
            if len(input) - chunk_size * (n_chunks - 1) > threshold:
                chunks.append(input[chunk_size * (n_chunks - 1) - overlap_size:])
            else:
                chunks[-1] += input[chunk_size * (n_chunks - 1):]
            
            return chunks
        
    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")

def _file_to_chunks(input: Dict[str, Any], 
                   field: str = 'content', 
                   chunk_size: int = 1500, 
                   overlap: float = 0.2, 
                   threshold: int = 200) -> List[Dict[str, Any]]:
    """
    Splits text from a specified dictionary field into chunks and returns a list of dictionaries.
    
    Args:
        input (Dict[str, Any]): The input dictionary containing the text field to be chunked.
        field (str, optional): The dictionary key corresponding to the text field. Defaults to 'content'.
        chunk_size (int, optional): Size of each text chunk in characters. Defaults to 1500.
        overlap (float, optional): Percentage of overlap between adjacent chunks, in the range [0, 1]. Defaults to 0.2.
        threshold (int, optional): Minimum size for the last chunk. If smaller, it will be merged with the previous chunk. Defaults to 200.
        
    Raises:
        ValueError: If any error occurs during the chunking process.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing a separate chunk along with original key-value pairs from the input dictionary.
    
    Example:
        >>> d = {'content': 'This is a test string.', 'other_field': 1}
        >>> file_to_chunks(d)
        [{'chunk_overlap': 0.2, 'chunk_threshold': 200, 'file_chunks': 2, 'chunk_id': 1, 'chunk_size': 14, 'chunk_content': 'This is a test', 'other_field': 1}, ...]
    """

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
                   field: str = 'content', 
                   chunk_size: int = 1500, 
                   overlap: float = 0.2, 
                   threshold: int = 200, 
                   to_csv=False, 
                   project='project',
                   output_dir='data/logs/sources/', 
                   chunk_func = _file_to_chunks,
                   filename=None, 
                   verbose=True, 
                   timestamp=True, 
                   logger=None):
    """
        Splits text from a specified dictionary field into chunks and returns a list of dictionaries.

    Args:
        input (List[Dict[str, Any]]): The input dictionaries containing the text field to be chunked.
        field (str, optional): The dictionary key corresponding to the text field. Defaults to 'content'.
        chunk_size (int, optional): Size of each text chunk in characters. Defaults to 1500.
        overlap (float, optional): Percentage of overlap between adjacent chunks, in the range [0, 1]. Defaults to 0.2.
        threshold (int, optional): Minimum size for the last chunk. If smaller, it will be merged with the previous chunk. Defaults to 200.
        to_csv: If True, export the processed data to a CSV file.
        project: The name of the project.
        output_dir: The directory path for exporting the CSV file.
        filename: The name of the CSV file.
        verbose: If True, print a verbose message after export.
        timestamp: If True, include a timestamp in the exported file name.
        logger: An optional DataLogger instance for logging.
    """
    
    f = lambda x: chunk_func(x, field=field, chunk_size=chunk_size, overlap=overlap, threshold=threshold)
    logs = to_list(l_call(input, f), flat=True)
    
    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logger = DataLogger(log=logs) if not logger else logger
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    """
    Get index of elements in a list based on their consecutive cumulative sum of length,
    according to some upper threshold. Return lists of indices as bins.
    
    Args:
    input (List[str]): List of items to be binned.
    upper (int, optional): Upper threshold for the cumulative sum of the length of items in a bin. Default is 7500.
    
    Returns:
    List[List[int]]: List of lists, where each inner list contains the indices of the items that form a bin.
    
    Example:
    >>> items = ['apple', 'a', 'b', 'banana', 'cheery', 'c', 'd', 'e']
    >>> upper = 10
    >>> get_bins(items, upper)
    [[0, 1, 2], [3], [4, 5, 6, 7]]
    """
    current = 0
    bins = []
    bin = []
    for idx, item in enumerate(input):
        if current + len(item) < upper:
            bin.append(idx)
            current += len(item)
        elif current + len(item) >= upper:
            bins.append(bin)
            bin = [idx]
            current = len(item)
        if idx == len(input) - 1 and len(bin) > 0:
            bins.append(bin)
    return bins
