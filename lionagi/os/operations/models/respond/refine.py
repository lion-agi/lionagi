from typing import Any, List, Optional, Sequence


class Refine:
    """Refine responses across compact text chunks."""

    def __init__(
        self, llm, prompt_helper, text_qa_template, refine_template, output_cls=None
    ):
        self.llm = llm
        self.prompt_helper = prompt_helper
        self.text_qa_template = text_qa_template
        self.refine_template = refine_template
        self.output_cls = output_cls

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        prev_response: Optional[str] = None,
        **response_kwargs: Any,
    ) -> str:
        compact_texts = self._make_compact_text_chunks(query_str, text_chunks)
        return await super().aget_response(
            query_str=query_str,
            text_chunks=compact_texts,
            prev_response=prev_response,
            **response_kwargs,
        )

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        prev_response: Optional[str] = None,
        **response_kwargs: Any,
    ) -> str:
        new_texts = self._make_compact_text_chunks(query_str, text_chunks)
        return super().get_response(
            query_str=query_str,
            text_chunks=new_texts,
            prev_response=prev_response,
            **response_kwargs,
        )

    def _make_compact_text_chunks(
        self, query_str: str, text_chunks: Sequence[str]
    ) -> List[str]:
        text_qa_template = self._text_qa_template.format(query_str=query_str)
        refine_template = self._refine_template.format(query_str=query_str)

        max_prompt = max(text_qa_template, refine_template, key=len)
        return self._prompt_helper.repack(max_prompt, text_chunks)

    async def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        prev_response: Optional[str] = None,
        **response_kwargs: Any,
    ) -> str:
        response = None
        for text_chunk in text_chunks:
            if prev_response is None:
                response = await self._agive_response_single(
                    query_str, text_chunk, **response_kwargs
                )
            else:
                response = await self._arefine_response_single(
                    prev_response, query_str, text_chunk, **response_kwargs
                )
            prev_response = response
        return response

    async def _give_response_single(
        self, query_str: str, text_chunk: str, **response_kwargs: Any
    ) -> str:
        text_qa_template = self.text_qa_template.format(query_str=query_str)
        text_chunks = self.prompt_helper.repack(text_qa_template, [text_chunk])

        for cur_text_chunk in text_chunks:
            response = await self.llm.apredict(
                text_qa_template, context_str=cur_text_chunk, **response_kwargs
            )
        return response

    async def _refine_response_single(
        self, response: str, query_str: str, text_chunk: str, **response_kwargs: Any
    ) -> str:
        fmt_text_chunk = text_chunk[:50]
        refine_template = self.refine_template.format(
            query_str=query_str, existing_answer=response
        )
        text_chunks = self.prompt_helper.repack(
            refine_template, text_chunks=[text_chunk]
        )

        for cur_text_chunk in text_chunks:
            structured_response = await self.llm.apredict(
                refine_template, context_msg=cur_text_chunk, **response_kwargs
            )
            response = structured_response.answer
        return response
