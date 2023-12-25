from typing import Dict, List, Any

from ...sys_util import to_list, l_call
from ...log_util import DataLogger


def _file_to_chunks(input: Dict[str, Any],
                   field: str = 'content',
                   chunk_size: int = 1500,
                   chunker = None,
                   overlap: float = 0.2,
                   threshold: int = 200) -> List[Dict[str, Any]]:
    try:
        out = {key: value for key, value in input.items() if key != field}
        out.update({"chunk_overlap": overlap, "chunk_threshold": threshold})

        chunks = chunker(input[field], chunk_size=chunk_size, overlap=overlap, threshold=threshold)
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

    _f = lambda x: chunk_func(x, field=field, chunk_size=chunk_size, overlap=overlap, threshold=threshold)
    logs = to_list(l_call(input, _f), flat=True)

    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logger = DataLogger(log=logs) if not logger else logger
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)

    return logs
