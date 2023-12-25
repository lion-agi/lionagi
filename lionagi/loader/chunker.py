import math
from typing import List, Union

def chunk_text(input: str, chunk_size: int, overlap: float,
               threshold: int) -> List[Union[str, None]]:
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
                chunks[-1] += input[chunk_size * (n_chunks - 1) + overlap_size:]

            return chunks

    except Exception as e:
        raise ValueError(f"An error occurred while chunking the text. {e}")
