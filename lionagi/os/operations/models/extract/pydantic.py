from typing import Any, Dict, List, Optional, Sequence

DEFAULT_EXTRACT_TEMPLATE_STR = """\
Here is the content of the section:
----------------
{context_str}
----------------
Given the contextual information, extract out a {class_name} object.\
"""


class PydanticProgramExtractor(BaseExtractor):
    def __init__(
        self,
        program: BasePydanticProgram,
        input_key: str = "input",
        extract_template_str: str = DEFAULT_EXTRACT_TEMPLATE_STR,
        num_workers: int = 5,
        **kwargs: Any,
    ):
        self.program = program
        self.input_key = input_key
        self.extract_template_str = extract_template_str
        self.num_workers = num_workers

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        program_jobs = [self._acall_program(node) for node in nodes]
        return await run_jobs(
            program_jobs, show_progress=False, workers=self.num_workers
        )

    async def _acall_program(self, node: BaseNode) -> Dict[str, Any]:
        if not isinstance(node, TextNode):
            return {}
        extract_str = self.extract_template_str.format(
            context_str=node.get_content(metadata_mode="text"),
            class_name=self.program.output_cls.__name__,
        )
        ret_object = await self.program.acall(**{self.input_key: extract_str})
        return ret_object.dict()
