from typing import Any, Dict, List, Optional, Sequence

DEFAULT_SUMMARY_EXTRACT_TEMPLATE = """\
Here is the content of the section:
{context_str}

Summarize the key topics and entities of the section. Summary: """

class SummaryExtractor(BaseExtractor):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        summaries: List[str] = ["self"],
        prompt_template: str = DEFAULT_SUMMARY_EXTRACT_TEMPLATE,
        num_workers: int = 5,
        **kwargs: Any,
    ):
        if not all(s in ["self", "prev", "next"] for s in summaries):
            raise ValueError("summaries must be one of ['self', 'prev', 'next']")
        self.llm = llm
        self.summaries = summaries
        self.prompt_template = prompt_template
        self.num_workers = num_workers
        self._self_summary = "self" in summaries
        self._prev_summary = "prev" in summaries
        self._next_summary = "next" in summaries

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        if not all(isinstance(node, TextNode) for node in nodes):
            raise ValueError("Only `TextNode` is allowed for `Summary` extractor")

        node_summaries_jobs = [self._agenerate_node_summary(node) for node in nodes]
        node_summaries = await run_jobs(node_summaries_jobs, show_progress=False, workers=self.num_workers)

        metadata_list: List[Dict] = [{} for _ in nodes]
        for i, metadata in enumerate(metadata_list):
            if i > 0 and self._prev_summary:
                metadata["prev_section_summary"] = node_summaries[i - 1]
            if i < len(nodes) - 1 and self._next_summary:
                metadata["next_section_summary"] = node_summaries[i + 1]
            if self._self_summary:
                metadata["section_summary"] = node_summaries[i]

        return metadata_list

    async def _agenerate_node_summary(self, node: BaseNode) -> str:
        if not isinstance(node, TextNode):
            return ""
        context_str = node.get_content(metadata_mode="text")
        summary = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template), context_str=context_str
        )
        return summary.strip()
