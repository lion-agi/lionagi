from typing import List, Union
import math



    
    
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
    return logs


    if to_csv:
        filename = filename if filename else f"{project}_sources.csv"
        logger = logger or DataLogger(log=logs)
        logger.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)