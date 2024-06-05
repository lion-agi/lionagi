from typing import Any, Dict, List, Optional, Sequence

DEFAULT_KEYWORD_EXTRACT_TEMPLATE = "{context_str}. Give {keywords} unique keywords for this document. Format as comma separated. Keywords: "

class KeywordExtractor(BaseExtractor):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        keywords: int = 5,
        prompt_template: str = DEFAULT_KEYWORD_EXTRACT_TEMPLATE,
        num_workers: int = 5,
        **kwargs: Any,
    ) -> None:
        if keywords < 1:
            raise ValueError("num_keywords must be >= 1")
        self.llm = llm
        self.keywords = keywords
        self.prompt_template = prompt_template
        self.num_workers = num_workers

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        keyword_jobs = [self._aextract_keywords_from_node(node) for node in nodes]
        return await run_jobs(keyword_jobs, show_progress=False, workers=self.num_workers)

    async def _aextract_keywords_from_node(self, node: BaseNode) -> Dict[str, str]:
        if not isinstance(node, TextNode):
            return {}
        context_str = node.get_content(metadata_mode="text")
        keywords = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template),
            keywords=self.keywords,
            context_str=context_str,
        )
        return {"excerpt_keywords": keywords.strip()}
