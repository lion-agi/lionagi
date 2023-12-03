import math
from pathlib import Path
from typing import Any, Dict, List, Union

from .sys_util import to_list, l_call
from .log_util import DataLogger


def dir_to_path(dir_, ext_, recursive=False, flat=True):
    """
    Get a list of file paths in the specified directory with the given extension.

    Args:
        dir_: The directory path.
        ext_: The file extension to filter.
        recursive: If True, search for files recursively in subdirectories.
        flat: If True, flatten the result into a single list.

    Example:
        >>> files = dir_to_path(dir_='my_directory', ext_='.txt', recursive=True, flat=True)
    """

    def _dir_to_path(ext, recursive=recursive):
        tem = '**/*' if recursive else '*'
        return list(Path(dir_).glob(tem + ext))
    
    return to_list(l_call(ext_, _dir_to_path, flat=True), flat=flat)

def read_text(file_path_: str, clean: bool = True) -> str:
    """
    Read the content of a text file and optionally clean it by removing specified characters.

    Args:
        file_path_ (str): The path to the text file.
        clean (bool): If True, clean the content by replacing specified characters.

    Returns:
        str: The content of the text file.

    Example:
        >>> content = read_text(file_path_='example.txt', clean=True)
    """

    with open(file_path_, 'r') as f:
        content = f.read()
        if clean:
            # Define characters to replace and their replacements
            replacements = {'\\': ' ', '\\\n': ' ', '\\\t': ' ', '  ': ' ', '\'': ' '}
            for old, new in replacements.items():
                content = content.replace(old, new)
        return content

def dir_to_files(dir_, ext_, recursive=False, reader=read_text, 
                 clean=True, to_csv=False, project='project',
                 output_dir='data/logs/sources/', filename=None, 
                 verbose=True, timestamp=True, logger=None):
    """
    Read and process files in the specified directory with the given extension.

    Args:
        dir_: The directory path.
        ext_: The file extension to filter.
        recursive (bool): If True, search for files recursively in subdirectories.
        reader: The function to read and process the content of each file.
        clean: If True, clean the content by replacing specified characters.
        to_csv: If True, export the processed data to a CSV file.
        project: The name of the project.
        output_dir: The directory path for exporting the CSV file.
        filename: The name of the CSV file.
        verbose: If True, print a verbose message after export.
        timestamp: If True, include a timestamp in the exported file name.
        logger: An optional DataLogger instance for logging.

    Example:
        >>> logs = dir_to_files(dir_='my_directory', ext_='.txt', to_csv=True)
    """

    sources = dir_to_path(dir_, ext_, recursive=recursive)
    
    def split_path(path_: Path) -> tuple:
        folder_name = path_.parent.name
        file_name = path_.name
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
        filename = filename if filename else f"{project}_sources.csv"
        logger = DataLogger(log=logs) if not logger else logger
        logger.to_csv(dir_=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs



def chunk_text(text: str, chunk_size: int, overlap: float, 
               threshold: int) -> List[Union[str, None]]:
    """
    Splits a string into chunks of a specified size, allowing for optional overlap between chunks.
    
    Args:
        text (str): The text to be split into chunks.
        chunk_size (int): The size of each chunk in characters.
        overlap (float): A value between [0, 1] specifying the percentage of overlap between adjacent chunks.
        threshold (int): The minimum size for the last chunk. If the last chunk is smaller than this, it will be merged with the previous chunk.
        
    Raises:
        TypeError: If input text cannot be converted to a string.
        ValueError: If any error occurs during the chunking process.
        
    Returns:
        List[Union[str, None]]: List of text chunks.
        
    Example:
        >>> chunk_text("This is a test string.", 10, 0.2, 5)
        ['This is a t', ' a test str', 'est string.']
    """
    
    try:
        # Ensure text is a string
        if not isinstance(text, str):
            text = str(text)
        
        chunks = []
        n_chunks = math.ceil(len(text) / chunk_size)
        overlap_size = int(chunk_size * overlap / 2)
        
        if n_chunks == 1:
            return [text]
        
        elif n_chunks == 2:
            chunks.append(text[:chunk_size + overlap_size])
            if len(text) - chunk_size > threshold:
                chunks.append(text[chunk_size - overlap_size:])
            else:
                return [text]
            return chunks
        
        elif n_chunks > 2:
            chunks.append(text[:chunk_size + overlap_size])
            for i in range(1, n_chunks - 1):
                start_idx = chunk_size * i - overlap_size
                end_idx = chunk_size * (i + 1) + overlap_size
                chunks.append(text[start_idx:end_idx])
            
            if len(text) - chunk_size * (n_chunks - 1) > threshold:
                chunks.append(text[chunk_size * (n_chunks - 1) - overlap_size:])
            else:
                chunks[-1] += text[chunk_size * (n_chunks - 1):]
            
            return chunks
        
    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")

def file_to_chunks(d: Dict[str, Any], 
                   field: str = 'content', 
                   chunk_size: int = 1500, 
                   overlap: float = 0.2, 
                   threshold: int = 200) -> List[Dict[str, Any]]:
    """
    Splits text from a specified dictionary field into chunks and returns a list of dictionaries.
    
    Args:
        d (Dict[str, Any]): The input dictionary containing the text field to be chunked.
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
        out = {key: value for key, value in d.items() if key != field}
        out.update({"chunk_overlap": overlap, "chunk_threshold": threshold})
        
        chunks = chunk_text(d[field], chunk_size=chunk_size, overlap=overlap, threshold=threshold)
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
    
def files_to_chunks(d, 
                   field: str = 'content', 
                   chunk_size: int = 1500, 
                   overlap: float = 0.2, 
                   threshold: int = 200, 
                   to_csv=False, 
                   project='project',
                   output_dir='data/logs/sources/', 
                   filename=None, 
                   verbose=True, 
                   timestamp=True, 
                   logger=None):
    """
        Splits text from a specified dictionary field into chunks and returns a list of dictionaries.

    Args:
        d (Dict[str, Any]): The input dictionary containing the text field to be chunked.
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
    
    f = lambda x: file_to_chunks(x, field=field, chunk_size=chunk_size, overlap=overlap, threshold=threshold)
    logs = to_list(l_call(d, f))
    
    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logger = DataLogger(log=logs) if not logger else logger
        logger.to_csv(dir_=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs


def get_bins(items: List[str], upper: int = 7500) -> List[List[int]]:
    """
    Get index of elements in a list based on their consecutive cumulative sum of length,
    according to some upper threshold. Return lists of indices as bins.
    
    Args:
    items (List[str]): List of items to be binned.
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
    for idx, item in enumerate(items):
        if current + len(item) < upper:
            bin.append(idx)
            current += len(item)
        elif current + len(item) >= upper:
            bins.append(bin)
            bin = [idx]
            current = len(item)
        if idx == len(items) - 1 and len(bin) > 0:
            bins.append(bin)
    return bins
