from typing import Any, List, Dict, Union
import pandas as pd
from .sys_util import is_same_dtype

def to_df(
    item: Any, how: str = 'all', drop_kwargs: Dict = {}, reset_index: bool = True, 
    **kwargs
) -> pd.DataFrame:
    try:
        dfs = ''
        
        if isinstance(item, List):
            if is_same_dtype(item, pd.DataFrame):
                dfs = pd.concat(item)
            dfs = pd.DataFrame(item)

        elif isinstance(item, pd.DataFrame):
            dfs = item

        drop_kwargs['how'] = how
        dfs = dfs.dropna(**drop_kwargs)
        
        if reset_index:
            drop = kwargs.pop('drop', True)
            inplace = kwargs.pop('inplace', True)
            dfs.reset_index(drop=drop, inplace=inplace, **kwargs)
            
        return dfs
    
    except Exception as e:
        raise ValueError(f'Error converting items to DataFrame: {e}')

def search_keywords(
    df,
    keywords: Union[str, list],
    col = "content",
    case_sensitive: bool = False, reset_index=False, dropna=False
):
    out = ''
    if isinstance(keywords, list):
        keywords = '|'.join(keywords)
    if not case_sensitive:
        out = df[
            df[col].str.contains(keywords, case=False)
        ]        
    out = df[df[col].str.contains(keywords)]
    if reset_index or dropna:
        out = to_df(out, reset_index=reset_index)
    return out

def replace_keyword(
    df,
    keyword: str, 
    replacement: str, 
    col='content',
    case_sensitive: bool = False
) -> None:
    if not case_sensitive:
        df[col] = df[col].str.replace(
            keyword, replacement, case=False
        )
    else:
        df[col] = df[col].str.replace(
            keyword, replacement
        )
        
def remove_last_n_rows(df, steps: int) -> None:
    if steps < 0 or steps > len(df):
        raise ValueError("Steps must be a non-negative integer less than or equal to the length of DataFrame.")
    df = to_df(df[:-steps])

def _update_row(
    df, col = "node_id", old_value = None,  new_value = None
) -> bool:
    index = df.index[df[col] == old_value].tolist()
    if index:
        df.at[index[0], col] = new_value
        return True
    return False
