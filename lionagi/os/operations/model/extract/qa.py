from typing import Any, Dict, List, Optional, Sequence

DEFAULT_QUESTION_GEN_TMPL = """\
Here is the context:
{context_str}

Given the contextual information, generate {num_questions} questions this context can provide specific answers to which are unlikely to be found elsewhere.

Higher-level summaries of surrounding context may be provided as well. Try using these summaries to generate better questions that this context can answer.
"""

class QuestionsAnsweredExtractor(BaseExtractor):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        questions: int = 5,
        prompt_template: str = DEFAULT_QUESTION_GEN_TMPL,
        embedding_only: bool = True,
        num_workers: int = 5,
        **kwargs: Any,
    ) -> None:
        if questions < 1:
            raise ValueError("questions must be >= 1")
        self.llm = llm
        self.questions = questions
        self.prompt_template = prompt_template
        self.embedding_only = embedding_only
        self.num_workers = num_workers

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        question_jobs = [self._aextract_questions_from_node(node) for node in nodes]
        return await run_jobs(question_jobs, show_progress=False, workers=self.num_workers)

    async def _aextract_questions_from_node(self, node: BaseNode) -> Dict[str, str]:
        if not isinstance(node, TextNode):
            return {}
        context_str = node.get_content(metadata_mode="text")
        questions = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template),
            num_questions=self.questions,
            context_str=context_str,
        )
        return {"questions_this_excerpt_can_answer": questions.strip()}
