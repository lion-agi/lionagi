from .sys_utils import flatten_list, to_list
from .return_utils import l_return
from pathlib import Path
import pandas as pd
import math

def to_csv(ouputs, filename):
    """
    Converts a list of objects to a pandas DataFrame and writes it to a csv file.
    
    Args:
        outputs (list): List of objects to be converted to a DataFrame.
        filename (str): Name of the csv file to write the DataFrame to.

    Returns:
        None
    """
    df = pd.DataFrame([i for i in ouputs if i is not None])
    df.reset_index(drop=True, inplace=True)
    df.to_csv(filename)
    
def _get_files(_dir, _ext, flatten):
    """
    Fetches the files from the directory with the given extensions. 
    
    The function takes in a directory path, extensions, and a boolean value for flatten. If flatten is True, 
    it flattens the returned list otherwise returns as is. It first converts the extensions to a list, checks if any 
    are provided. Depending on the flatten value, it fetches all the files with the given _ext from the _dir directory, 
    and then returns the list of files. The path of each file is converted to a pathlib.Path object.
    
    Args:
        _dir (str/Pathlib.Path): The directory path where to look for files.
        _ext (list/str): The extensions of the files to include. 
        flatten (bool): If True, the returned list of files will be flattened.
        
    Returns:
        list: A list of pathlib.Path objects representing the files in the directory with the given extensions.
    """
    rtn = ''
    if len(to_list(_ext)) > 0:
        f1 = lambda x: [file for file in [x.glob('**/*' + ext) for ext in _ext]]
        f2 = lambda x: [Path(file) for file in x]
        rtn = l_return(l_return(_dir, f1)[0], f2)
        return flatten_list(rtn) if flatten else rtn


def _get_all_files(_dir, _ext, flatten_inside=True, faltten_outside=False):
    """
    Description: This function retrieves all files with the given extension from a particular directory. Results can be flatted or left nested depending on the boolean flags.

    Args:
    _dir (str): File directory.
    _ext (str): File extensions to get.
    flatten_inside (bool): If True, flattens the inner lists.
    faltten_outside (bool): If True, flattens all lists outside inner ones.

    Returns:
    list: A list of all files with the given extensions in the directory.
    """
    a = l_return(_dir, lambda x: _get_files(x, _ext, flatten=flatten_inside))
    return flatten_list(a) if faltten_outside else a

def _read_as_text(filepath, clean):
    """
    Description: Opens a file and reads its content as a text file. Option to clean file content by replacing certain characters.

    Args:
    filepath (str): Path to the file to be read.
    clean (bool): If True, cleans text by replacing '\\','\\\n','\\\t','  ','\'' characters with a space.

    Returns:
    string: File content as text.
    """
    with open(filepath, 'r') as f:
        if clean:
            a = f.read().replace('\\', ' ')
            a = a.replace('\\\n',' ')
            a = a.replace('\\\t',' ')
            a = a.replace('  ',' ')
            a = a.replace('\'',' ')
            return a
        else:
            return f.read()
        
def dir_to_dict(_dir, _ext, read_as=_read_as_text, flatten=True, clean=True, to_csv=False, output_dir='data/logs/sources/', filename='autogen_py.csv', verbose=True, timestamp=True, logger=None):
    """
    Description: Reads all files of required extension from source folders into a list of dictionaries.

    Args:
    _dir (str): Directory path.
    _ext (str): File extensions to read.
    read_as (function): Function to read file content, default is _read_as_text.
    flatten (bool): If True, returns a flattened list, else a nested list.
    clean (bool): If True, cleans file content as defined in the _read_as_text function.
    to_csv (bool): If True, logs the output to a csv file.
    output_dir (str): Output directory for csv file, if to_csv=True.
    filename (str): Name of output csv file, if to_csv=True.
    verbose (bool): If True, prints verbose logs.
    timestamp (bool): If True, adds timestamp to logs.

    Returns:
    list: List of dictionary objects with keys - 'folder', 'file', 'content'.
    """
    _sources = _get_all_files(_dir, _ext, faltten_outside=flatten)    
    def _split(_path):
        _folder_name =  str(_path).split('/')[-2]
        _file_name = str(_path).split('/')[-1]
        return (_folder_name, _file_name)
    def _to_dict(_path):
        _folder, _file = _split(_path)
        out = {
            "folder": _folder,
            "file": _file,
            "content": read_as(_path, clean=clean)}
        if len(out['content']) > 0:
            return out
    if to_csv:
        logger.log = l_return(_sources, _to_dict)
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)
    if flatten:
        return l_return(_sources, _to_dict)
    else:
        return l_return(_sources, lambda x: l_return(x, _to_dict))
    



def _split_text(text: str, chunk_size: int, overlap: float, threshold: int) -> list[str|None]:
    """
    Summary: 
        Splits text into chunks of equal size with overlap. A basic text spliter. If the file is shorter than chunk_size it won't be chunked, if the last chunk is shorter than threshold it will be merged with the previous chunk.
    
    Length of Chunks:
        overlap_size = (chunk_size * overlap / 2).
        Beginning chunk = (chunk_size + overlap_size).
        Middle chunks = (chunk_size + overlap_size*2).
        Last chunk = (overlap_size + remainder) if remainder > threshold, else it will be merged with the previous chunk.
    
    Args:
        _text (str): text to be splitted
        chunk_size (int): chunk size in characters
        overlap (float): overlap among chunks as a percentage of chunk_size between [0,1]. Each chunk will get extra overlap_size on both side if possible.
        threshold (int): minimum size for the remainder as last chunk.

    Raises:
        TypeError: if input cannot be converted to string. 
        ValueError: if error occurs during splitting.

    Returns:
        _type_: _description_
    """
    
    # convert input to string if possible
    if not isinstance(text, str):
        try: 
            text = str(text)
        except Exception as e:
            raise TypeError(f"Expected type str, got {type(text)}.{e}")
    try:
        chunks = []
        num_chunks = math.ceil(len(text) / chunk_size)
        overlap_size = int(chunk_size * overlap / 2)
        
        # return the whole text as a list if it is shorter than chunk_size
        if num_chunks == 1:
            return [text]
        
        # return the text as list of two chunks if the remainder if larger than threshold
        # otherwise return the whole text as a list
        elif num_chunks == 2:
            chunks.append(text[:chunk_size+overlap_size])
            if len(text) - chunk_size > threshold:
                chunks.append(text[chunk_size-overlap_size:])
                return chunks
            else:
                return [text]
        
        # return the text as a list of multiple chunks
        # if the remainder is larger than threshold, return the last chunk as a separate chunk
        # otherwise merge the last chunk with the previous chunk
        elif num_chunks > 2:
            chunks.append(text[:chunk_size+overlap_size])
            for i in range(1, num_chunks-1):
                chunks.append(text[(chunk_size*i-overlap_size):(chunk_size*(i+1) + overlap_size)])
            if len(text) - (chunk_size*(num_chunks-1)) > threshold:
                chunks.append(text[(chunk_size*(num_chunks-1)-overlap_size):])
            else:
                chunks[-1] += text[-(len(text) - (chunk_size*(num_chunks-1))):]
            return chunks
    
    # raise error if any error occurs during splitting    
    except Exception as e:
        raise ValueError(f"Error splitting text into chunks. {e}")


def get_chunks(_dict: dict, field='content', chunk_size=1500, overlap=0.2, threshold=200) -> list[dict]:
    """
    Summary: 
        Splits texts to chunks from dictionary. This is specifically written for chunking python code files. 
        
    Args:
        dict (dict): The dictionary who's field key needs to be chunked.
        field (str, optional): The field key that needs to be chunked. Defaults to 'content'.
        dict_format (function, optional): A function that takes in a dictionary and returns a dictionary. Defaults is all fields in the input dictionar and all kwags.
        kwags: keyword arguments to be passed into _split_text function. If need to customize, need to pass in the whole kwags as dict
            - chunk_size (int): chunk size in characters, default 2000.
            - overlap (float): overlap among chunks as a percentage of chunk_size between [0,1]. Each chunk will get extra overlap_size on both side if possible. default is 0.2.
            - threshold (int): minimum size for the remainder as last chunk. default is 200.

    Returns:
        list: A list of dictionaries, each containing a separate chunk and its corresponding details.
    """
    _out = {key:value for key, value in _dict.items() if key != field}
    _out.update({"chunk_size":chunk_size, "chunk_overlap":overlap, "chunk_threshold": threshold})
    
    # split text into chunks,
    try: 
        splited_chunks = _split_text(_dict[field], chunk_size=chunk_size, overlap=overlap, threshold=threshold)
        outs=[]
        for i, j in enumerate(splited_chunks):
            out = _out.copy()
            out.update({'chunk_id': i, field: j})     
            outs.append(out)
        return outs
    except Exception as e:
        raise ValueError(f"Error in splitting text. {e}")