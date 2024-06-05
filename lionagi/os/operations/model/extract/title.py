from typing import Any, Dict, List, Optional, Sequence

DEFAULT_TITLE_NODE_TEMPLATE = "Context: {context_str}. Give a title that summarizes all of the unique entities, titles or themes found in the context. Title: "
DEFAULT_TITLE_COMBINE_TEMPLATE = "{context_str}. Based on the above candidate titles and content, what is the comprehensive title for this document? Title: "

class TitleExtractor(BaseExtractor):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        nodes: int = 5,
        node_template: str = DEFAULT_TITLE_NODE_TEMPLATE,
        combine_template: str = DEFAULT_TITLE_COMBINE_TEMPLATE,
        num_workers: int = 5,
        **kwargs: Any,
    ) -> None:
        if nodes < 1:
            raise ValueError("num_nodes must be >= 1")
        self.llm = llm
        self.nodes = nodes
        self.node_template = node_template
        self.combine_template = combine_template
        self.num_workers = num_workers

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        nodes_by_doc_id = self.separate_nodes_by_ref_id(nodes)
        titles_by_doc_id = await self.extract_titles(nodes_by_doc_id)
        return [{"document_title": titles_by_doc_id[node.ref_doc_id]} for node in nodes]

    def filter_nodes(self, nodes: Sequence[BaseNode]) -> List[BaseNode]:
        return [node for node in nodes if isinstance(node, TextNode)]

    def separate_nodes_by_ref_id(self, nodes: Sequence[BaseNode]) -> Dict:
        separated_items: Dict[Optional[str], List[BaseNode]] = {}
        for node in nodes:
            key = node.ref_doc_id
            if key not in separated_items:
                separated_items[key] = []
            if len(separated_items[key]) < self.nodes:
                separated_items[key].append(node)
        return separated_items

    async def extract_titles(self, nodes_by_doc_id: Dict) -> Dict:
        titles_by_doc_id = {}
        for key, nodes in nodes_by_doc_id.items():
            title_candidates = await self.get_title_candidates(nodes)
            combined_titles = ", ".join(title_candidates)
            titles_by_doc_id[key] = await self.llm.apredict(
                PromptTemplate(template=self.combine_template),
                context_str=combined_titles,
            )
        return titles_by_doc_id

    async def get_title_candidates(self, nodes: List[BaseNode]) -> List[str]:
        title_jobs = [
            self.llm.apredict(
                PromptTemplate(template=self.node_template),
                context_str=node.text,
            )
            for node in nodes
        ]
        return await run_jobs(title_jobs, show_progress=False, workers=self.num_workers)
