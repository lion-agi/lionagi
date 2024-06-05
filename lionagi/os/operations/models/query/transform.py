"""Query Transformation Classes and Utilities."""

import dataclasses
from abc import abstractmethod
from typing import Any, Dict, Optional, cast

from core.base.query_pipeline.query import (
    ChainableMixin,
    InputKeys,
    OutputKeys,
    QueryComponent,
    validate_and_convert_stringable,
)
from core.base.response.schema import Response
from core.bridge.pydantic import Field
from core.prompts.default_prompts import DEFAULT_HYDE_PROMPT
from core.prompts.mixin import (
    PromptDictType,
    PromptMixin,
    PromptMixinType,
)
from core.schema import QueryBundle, QueryType
from core.service_context_elements.llm_predictor import (
    LLMPredictorType,
)
from core.settings import Settings
from core.utils import print_text


class BaseQueryTransform(ChainableMixin, PromptMixin):
    """Base class for query transformations to enhance index querying."""

    def _get_prompt_modules(self) -> PromptMixinType:
        """Retrieve prompt modules."""
        return {}

    @abstractmethod
    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Execute the query transformation."""

    def run(
        self,
        query_bundle_or_str: QueryType,
        metadata: Optional[Dict] = None,
    ) -> QueryBundle:
        """Run the query transformation."""
        metadata = metadata or {}
        if isinstance(query_bundle_or_str, str):
            query_bundle = QueryBundle(
                query_str=query_bundle_or_str,
                custom_embedding_strs=[query_bundle_or_str],
            )
        else:
            query_bundle = query_bundle_or_str

        return self._run(query_bundle, metadata=metadata)

    def __call__(
        self,
        query_bundle_or_str: QueryType,
        metadata: Optional[Dict] = None,
    ) -> QueryBundle:
        """Execute the query transformation."""
        return self.run(query_bundle_or_str, metadata=metadata)

    def _as_query_component(self, **kwargs: Any) -> QueryComponent:
        """Convert to a query component."""
        return QueryTransformComponent(query_transform=self)


class IdentityQueryTransform(BaseQueryTransform):
    """A no-op query transformation."""

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Return the query bundle unchanged."""
        return query_bundle


class HyDEQueryTransform(BaseQueryTransform):
    """Generates hypothetical documents for the query using an LLM."""

    def __init__(
        self,
        llm: Optional[LLMPredictorType] = None,
        hyde_prompt: Optional[BasePromptTemplate] = None,
        include_original: bool = True,
    ) -> None:
        """Initialize with an optional LLM and prompt."""
        super().__init__()

        self._llm = llm or Settings.llm
        self._hyde_prompt = hyde_prompt or DEFAULT_HYDE_PROMPT
        self._include_original = include_original

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {"hyde_prompt": self._hyde_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "hyde_prompt" in prompts:
            self._hyde_prompt = prompts["hyde_prompt"]

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Generate hypothetical documents for the query."""
        query_str = query_bundle.query_str
        hypothetical_doc = self._llm.predict(self._hyde_prompt, context_str=query_str)
        embedding_strs = [hypothetical_doc]
        if self._include_original:
            embedding_strs.extend(query_bundle.embedding_strs)
        return QueryBundle(
            query_str=query_str,
            custom_embedding_strs=embedding_strs,
        )


class DecomposeQueryTransform(BaseQueryTransform):
    """Decomposes a query into subqueries based on the index structure."""

    def __init__(
        self,
        llm: Optional[LLMPredictorType] = None,
        decompose_query_prompt: Optional[BasePromptTemplate] = None,
        verbose: bool = False,
    ) -> None:
        """Initialize with an optional LLM and prompt."""
        super().__init__()
        self._llm = llm or Settings.llm
        self._decompose_query_prompt = (
            decompose_query_prompt or DEFAULT_DECOMPOSE_QUERY_TRANSFORM_PROMPT
        )
        self.verbose = verbose

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {"decompose_query_prompt": self._decompose_query_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "decompose_query_prompt" in prompts:
            self._decompose_query_prompt = prompts["decompose_query_prompt"]

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Decompose the query based on index summary."""
        index_summary = cast(str, metadata.get("index_summary", "None"))
        query_str = query_bundle.query_str
        new_query_str = self._llm.predict(
            self._decompose_query_prompt,
            query_str=query_str,
            context_str=index_summary,
        )

        if self.verbose:
            print_text(f"> Current query: {query_str}\n", color="yellow")
            print_text(f"> New query: {new_query_str}\n", color="pink")

        return QueryBundle(
            query_str=new_query_str,
            custom_embedding_strs=[new_query_str],
        )


class ImageOutputQueryTransform(BaseQueryTransform):
    """Adds instructions for formatting image output in the query."""

    def __init__(
        self,
        width: int = 400,
        query_prompt: Optional[BasePromptTemplate] = None,
    ) -> None:
        """Initialize with desired image width and optional custom prompt."""
        self._width = width
        self._query_prompt = query_prompt or DEFAULT_IMAGE_OUTPUT_PROMPT

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {"query_prompt": self._query_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "query_prompt" in prompts:
            self._query_prompt = prompts["query_prompt"]

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Format the query to include image output instructions."""
        del metadata  # Unused
        new_query_str = self._query_prompt.format(
            query_str=query_bundle.query_str, image_width=self._width
        )
        return dataclasses.replace(query_bundle, query_str=new_query_str)


class StepDecomposeQueryTransform(BaseQueryTransform):
    """Decomposes a query into subqueries considering the index structure and previous reasoning."""

    def __init__(
        self,
        llm: Optional[LLMPredictorType] = None,
        step_decompose_query_prompt: Optional[BasePromptTemplate] = None,
        verbose: bool = False,
    ) -> None:
        """Initialize with an optional LLM and prompt."""
        super().__init__()
        self._llm = llm or Settings.llm
        self._step_decompose_query_prompt = (
            step_decompose_query_prompt or DEFAULT_STEP_DECOMPOSE_QUERY_TRANSFORM_PROMPT
        )
        self.verbose = verbose

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {"step_decompose_query_prompt": self._step_decompose_query_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "step_decompose_query_prompt" in prompts:
            self._step_decompose_query_prompt = prompts["step_decompose_query_prompt"]

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Decompose the query based on index summary and previous reasoning."""
        index_summary = cast(str, metadata.get("index_summary", "None"))
        prev_reasoning = cast(Response, metadata.get("prev_reasoning"))
        fmt_prev_reasoning = f"\n{prev_reasoning}" if prev_reasoning else "None"

        query_str = query_bundle.query_str
        new_query_str = self._llm.predict(
            self._step_decompose_query_prompt,
            prev_reasoning=fmt_prev_reasoning,
            query_str=query_str,
            context_str=index_summary,
        )
        if self.verbose:
            print_text(f"> Current query: {query_str}\n", color="yellow")
            print_text(f"> New query: {new_query_str}\n", color="pink")
        return QueryBundle(
            query_str=new_query_str,
            custom_embedding_strs=query_bundle.custom_embedding_strs,
        )


class FeedbackQueryTransformation(BaseQueryTransform):
    """Transforms the query based on evaluation feedback."""

    def __init__(
        self,
        llm: Optional[LLMPredictorType] = None,
        resynthesize_query: bool = False,
        resynthesis_prompt: Optional[BasePromptTemplate] = None,
    ) -> None:
        """Initialize with optional LLM and resynthesis prompt."""
        super().__init__()
        self.llm = llm or Settings.llm
        self.should_resynthesize_query = resynthesize_query
        self.resynthesis_prompt = resynthesis_prompt or DEFAULT_RESYNTHESIS_PROMPT

    def _get_prompts(self) -> PromptDictType:
        """Retrieve prompts."""
        return {"resynthesis_prompt": self.resynthesis_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "resynthesis_prompt" in prompts:
            self.resynthesis_prompt = prompts["resynthesis_prompt"]

    def _run(self, query_bundle: QueryBundle, metadata: Dict) -> QueryBundle:
        """Transform the query based on evaluation feedback."""
        orig_query_str = query_bundle.query_str
        evaluation = metadata.get("evaluation")

        if evaluation and isinstance(evaluation, Evaluation):
            response = evaluation.response
            feedback = evaluation.feedback

            if feedback in ["YES", "NO"]:
                new_query = (
                    orig_query_str
                    + "\n----------------\n"
                    + self._construct_feedback(response)
                )
            else:
                if self.should_resynthesize_query:
                    new_query_str = self._resynthesize_query(
                        orig_query_str, response, feedback
                    )
                else:
                    new_query_str = orig_query_str
                new_query = (
                    self._construct_feedback(response)
                    + "\n"
                    + "Here is some feedback from the evaluator about the response given.\n"
                    + feedback
                    + "\n"
                    + "Now answer the question.\n"
                    + new_query_str
                )
            return QueryBundle(new_query, custom_embedding_strs=[orig_query_str])
        else:
            raise ValueError(
                "Evaluation is not properly set or is missing required fields."
            )

    @staticmethod
    def _construct_feedback(response: Optional[str]) -> str:
        """Construct feedback based on the response."""
        return f"Here is a previous answer:\n{response}" if response else ""

    def _resynthesize_query(
        self, query_str: str, response: str, feedback: Optional[str]
    ) -> str:
        """Resynthesize the query based on feedback."""
        if feedback is None:
            return query_str
        else:
            new_query_str = self.llm.predict(
                self.resynthesis_prompt,
                query_str=query_str,
                response=response,
                feedback=feedback,
            )
            return new_query_str


class QueryTransformComponent(QueryComponent):
    """Component for transforming queries in a query pipeline."""

    query_transform: BaseQueryTransform = Field(..., description="Query transform.")

    class Config:
        arbitrary_types_allowed = True

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set the callback manager."""
        # Not implemented

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the inputs for the component."""
        if "query_str" not in input:
            raise ValueError("Input must include 'query_str'")
        input["query_str"] = validate_and_convert_stringable(input["query_str"])
        input["metadata"] = input.get("metadata", {})
        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run the component with the given inputs."""
        output = self.query_transform.run(
            kwargs["query_str"],
            metadata=kwargs["metadata"],
        )
        return {"query_str": output.query_str}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Asynchronously run the component."""
        # Asynchronous execution not implemented
        return self._run_component(**kwargs)

    @property
    def input_keys(self) -> InputKeys:
        """Retrieve input keys."""
        return InputKeys.from_keys({"query_str"}, optional_keys={"metadata"})

    @property
    def output_keys(self) -> OutputKeys:
        """Retrieve output keys."""
        return OutputKeys.from_keys({"query_str"})
