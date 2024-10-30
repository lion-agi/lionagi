import math

import tiktoken

from .ln_convert import to_str
from .special_tokens import disallowed_tokens


class TokenizeUtil:

    @staticmethod
    def tokenize(
        text,
        encoding_model=None,
        encoding_name=None,
        return_byte=False,
        disallowed_tokens=disallowed_tokens,
    ):
        encoding = None

        if encoding_model:
            try:
                encoding_name = tiktoken.encoding_name_for_model(
                    encoding_model
                )
            except:
                encoding_name = encoding_name or "cl100k_base"

        if (
            not encoding_name
            or encoding_name in tiktoken.list_encoding_names()
        ):
            encoding_name = encoding_name or "cl100k_base"
            encoding = tiktoken.get_encoding(encoding_name)

        special_encodings = (
            [encoding.encode(token) for token in disallowed_tokens]
            if disallowed_tokens
            else []
        )
        codes = encoding.encode(text)
        if special_encodings and len(special_encodings) > 0:
            codes = [code for code in codes if code not in special_encodings]

        if return_byte:
            return codes

        return [encoding.decode([code]) for code in codes]

    @staticmethod
    def chunk_by_chars(
        text: str, chunk_size: int, overlap: float, threshold: int
    ) -> list[str | None]:
        """
        Chunks the input text into smaller parts, with optional overlap and threshold for final chunk.

        Parameters:
            text (str): The input text to chunk.

            chunk_size (int): The size of each chunk.

            overlap (float): The amount of overlap between chunks.

            threshold (int): The minimum size of the final chunk.

        Returns:
            List[Union[str, None]]: A list of text chunks.

        Raises:
            ValueError: If an error occurs during chunking.
        """

        def _chunk_n1():
            return [text]

        def _chunk_n2():
            chunks = []
            chunks.append(text[: chunk_size + overlap_size])

            if len(text) - chunk_size > threshold:
                chunks.append(text[chunk_size - overlap_size :])
            else:
                return _chunk_n1()

            return chunks

        def _chunk_n3():
            chunks = []
            chunks.append(text[: chunk_size + overlap_size])
            for i in range(1, n_chunks - 1):
                start_idx = chunk_size * i - overlap_size
                end_idx = chunk_size * (i + 1) + overlap_size
                chunks.append(text[start_idx:end_idx])

            if len(text) - chunk_size * (n_chunks - 1) > threshold:
                chunks.append(
                    text[chunk_size * (n_chunks - 1) - overlap_size :]
                )
            else:
                chunks[-1] += text[
                    chunk_size * (n_chunks - 1) + overlap_size :
                ]

            return chunks

        try:
            if not isinstance(text, str):
                text = to_str(text)

            n_chunks = math.ceil(len(text) / chunk_size)
            overlap_size = int(overlap / 2)

            if n_chunks == 1:
                return _chunk_n1()

            elif n_chunks == 2:
                return _chunk_n2()

            elif n_chunks > 2:
                return _chunk_n3()

        except Exception as e:
            raise ValueError(f"An error occurred while chunking the text. {e}")

    @staticmethod
    def chunk_by_tokens(
        text: str,
        chunk_size: int,
        overlap: float,
        threshold: int,  # minimum size of the final chunk in number of tokens
        encoding_model=None,
        encoding_name=None,
        return_tokens=False,
        return_byte=False,
    ) -> list[str | None]:

        tokens = TokenizeUtil.tokenize(
            text, encoding_model, encoding_name, return_byte=return_byte
        )

        n_chunks = math.ceil(len(tokens) / chunk_size)
        overlap_size = int(overlap * chunk_size / 2)
        residue = len(tokens) % chunk_size

        if n_chunks == 1:
            return text if not return_tokens else [tokens]

        elif n_chunks == 2:
            chunks = [tokens[: chunk_size + overlap_size]]
            if residue > threshold:
                chunks.append(tokens[chunk_size - overlap_size :])
                return (
                    [" ".join(chunk).strip() for chunk in chunks]
                    if not return_tokens
                    else chunks
                )
            else:
                return text if not return_tokens else [tokens]

        elif n_chunks > 2:
            chunks = []
            chunks.append(tokens[: chunk_size + overlap_size])
            for i in range(1, n_chunks - 1):
                start_idx = chunk_size * i - overlap_size
                end_idx = chunk_size * (i + 1) + overlap_size
                chunks.append(tokens[start_idx:end_idx])

            if len(tokens) - chunk_size * (n_chunks - 1) > threshold:
                chunks.append(
                    tokens[chunk_size * (n_chunks - 1) - overlap_size :]
                )
            else:
                chunks[-1] += tokens[-residue:]

            return (
                [" ".join(chunk) for chunk in chunks]
                if not return_tokens
                else chunks
            )
