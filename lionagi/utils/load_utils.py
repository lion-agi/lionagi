import math
from pathlib import Path
from typing import List, Union

from .type_utils import to_list
from .call_utils import l_call


def dir_to_path(dir: str, ext, recursive: bool = False, flat: bool = True):
    
    def _dir_to_path():
        tem = '**/*' if recursive else '*'
        return list(Path(dir).glob(tem + ext))
    
    try: 
        return to_list(l_call(ext, _dir_to_path, flat=True), flat=flat)
    except: 
        raise ValueError("Invalid directory or extension, please check the path")

def chunk_text(input: str, 
               chunk_size: int, 
               overlap: float,
               threshold: int) -> List[Union[str, None]]:
    
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
        overlap_size = int(chunk_size * overlap / 2)

        if n_chunks == 1: 
            return _chunk_n1()
        
        elif n_chunks == 2:
            return _chunk_n2()
        
        elif n_chunks > 2:
            return _chunk_n3()

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")

def read_text(filepath: str, clean: bool = True) -> str:
    with open(filepath, 'r') as f:
        content = f.read()
        if clean:
            # Define characters to replace and their replacements
            replacements = {'\\': ' ', '\n': ' ', '\t': ' ', '  ': ' ', '\'': ' '}
            for old, new in replacements.items():
                content = content.replace(old, new)
        return content