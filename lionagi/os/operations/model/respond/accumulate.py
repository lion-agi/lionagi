from typing import Any, List, Optional, Sequence


class Accumulate:
    """Accumulate responses across compact text chunks."""

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        separator: str = "\n---------------------\n",
        **response_kwargs: Any,
    ) -> str:
        text_qa_template = self._text_qa_template.format(query_str=query_str)
        new_texts = self._prompt_helper.repack(text_qa_template, text_chunks)

        return await super().aget_response(
            query_str=query_str,
            text_chunks=new_texts,
            separator=separator,
            **response_kwargs,
        )

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        separator: str = "\n---------------------\n",
        **response_kwargs: Any,
    ) -> str:
        text_qa_template = self._text_qa_template.format(query_str=query_str)
        new_texts = self._prompt_helper.repack(text_qa_template, text_chunks)

        return super().get_response(
            query_str=query_str,
            text_chunks=new_texts,
            separator=separator,
            **response_kwargs,
        )
