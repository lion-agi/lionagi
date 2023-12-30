import math
from pathlib import Path
from typing import List, Union

from .type_utils import to_list
from .call_utils import l_call

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    """
    Get index of elements in a list based on their consecutive cumulative sum of length,
    according to some upper threshold. Return lists of indices as bins.
    
    Parameters:
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

def dir_to_path(dir: str, ext, recursive: bool = False, flat: bool = True):
    
    def _dir_to_path():
        tem = '**/*' if recursive else '*'
        return list(Path(dir).glob(tem + ext))
    
    try: 
        return to_list(l_call(ext, _dir_to_path, flat=True), flat=flat)
    except: 
        raise ValueError("Invalid directory or extension, please check the path")

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
