from typing import Any, List, Optional, Sequence


class StructuredRefineResponse:
    """Represents a refined response to a query."""

    def __init__(self, answer: str, query_satisfied: bool):
        self.answer = answer
        self.query_satisfied = query_satisfied


class SimpleSummarize:
    def __init__(self, llm, prompt_helper, text_qa_template):
        self.llm = llm
        self.prompt_helper = prompt_helper
        self.text_qa_template = text_qa_template

    async def aget_response(
        self, query_str: str, text_chunks: Sequence[str], **response_kwargs: Any
    ) -> str:
        text_qa_template = self.text_qa_template.format(query_str=query_str)
        single_text_chunk = "\n".join(text_chunks)
        truncated_chunks = self.prompt_helper.truncate(
            prompt=text_qa_template, text_chunks=[single_text_chunk]
        )

        response = await self.llm.apredict(
            text_qa_template, context_str=truncated_chunks, **response_kwargs
        )
        return response or "Empty Response"


class TreeSummarize:
    def __init__(
        self, llm, prompt_helper, summary_template, use_async=False, verbose=False
    ):
        self.llm = llm
        self.prompt_helper = prompt_helper
        self.summary_template = summary_template
        self.use_async = use_async
        self.verbose = verbose

    async def get_response(
        self, query_str: str, text_chunks: Sequence[str], **response_kwargs: Any
    ) -> str:
        summary_template = self.summary_template.format(query_str=query_str)
        text_chunks = self.prompt_helper.repack(
            summary_template, text_chunks=text_chunks
        )

        if len(text_chunks) == 1:
            response = await self.llm.apredict(
                summary_template, context_str=text_chunks[0], **response_kwargs
            )
            return response

        else:
            tasks = [
                self.llm.apredict(
                    summary_template, context_str=text_chunk, **response_kwargs
                )
                for text_chunk in text_chunks
            ]
            summary_responses = await asyncio.gather(*tasks)
            summaries = [summary.json() for summary in summary_responses]

            return await self.aget_response(
                query_str=query_str, text_chunks=summaries, **response_kwargs
            )
