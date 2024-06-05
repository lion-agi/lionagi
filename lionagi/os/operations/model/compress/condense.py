from abc import ABC, abstractmethod
from typing import List, Optional, Union
from enum import Enum


class BaseChatEngine(ABC):
    """Base Chat Engine."""

    @abstractmethod
    def reset(self) -> None:
        """Reset conversation state."""

    @abstractmethod
    def chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> "AgentChatResponse":
        """Main chat interface."""

    @abstractmethod
    def stream_chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> "StreamingAgentChatResponse":
        """Stream chat interface."""

    @abstractmethod
    async def achat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> "AgentChatResponse":
        """Async version of main chat interface."""

    @abstractmethod
    async def astream_chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> "StreamingAgentChatResponse":
        """Async version of stream chat interface."""

    @property
    @abstractmethod
    def chat_history(self) -> List["ChatMessage"]:
        """Get chat history."""


import asyncio
from typing import List, Optional, Type


class SimpleChatEngine(BaseChatEngine):
    """
    Simple Chat Engine.

    Have a conversation with the LLM.
    This does not make use of a knowledge base.
    """

    def __init__(
        self, llm: LLM, memory: BaseMemory, prefix_messages: List[ChatMessage]
    ):
        self._llm = llm
        self._memory = memory
        self._prefix_messages = prefix_messages

    @classmethod
    def from_defaults(
        cls,
        chat_history: Optional[List[ChatMessage]] = None,
        memory: Optional[BaseMemory] = None,
        memory_cls: Type[BaseMemory] = ChatMemoryBuffer,
        system_prompt: Optional[str] = None,
        prefix_messages: Optional[List[ChatMessage]] = None,
        llm: Optional[LLM] = None,
        **kwargs,
    ):
        llm = llm or LLM.from_defaults()
        chat_history = chat_history or []
        memory = memory or memory_cls.from_defaults(chat_history=chat_history, llm=llm)
        if system_prompt:
            prefix_messages = [
                ChatMessage(content=system_prompt, role=llm.metadata.system_role)
            ]
        return cls(llm, memory, prefix_messages or [])

    def chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        all_messages = self._prefix_messages + self._memory.get()
        chat_response = self._llm.chat(all_messages)
        ai_message = chat_response.message
        self._memory.put(ai_message)
        return AgentChatResponse(response=str(chat_response.message.content))

    def stream_chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> StreamingAgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        all_messages = self._prefix_messages + self._memory.get()
        chat_response = StreamingAgentChatResponse(
            chat_stream=self._llm.stream_chat(all_messages)
        )
        return chat_response

    async def achat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        all_messages = self._prefix_messages + self._memory.get()
        chat_response = await self._llm.achat(all_messages)
        ai_message = chat_response.message
        self._memory.put(ai_message)
        return AgentChatResponse(response=str(chat_response.message.content))

    async def astream_chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> StreamingAgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        all_messages = self._prefix_messages + self._memory.get()
        chat_response = StreamingAgentChatResponse(
            achat_stream=await self._llm.astream_chat(all_messages)
        )
        return chat_response

    def reset(self) -> None:
        self._memory.reset()

    @property
    def chat_history(self) -> List[ChatMessage]:
        return self._memory.get_all()


from typing import List, Optional, Tuple


class ContextChatEngine(BaseChatEngine):
    """
    Context Chat Engine.

    Uses a retriever to retrieve a context, set the context in the system prompt,
    and then uses an LLM to generate a response, for a fluid chat experience.
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        llm: LLM,
        memory: BaseMemory,
        prefix_messages: List[ChatMessage],
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        context_template: Optional[str] = None,
    ):
        self._retriever = retriever
        self._llm = llm
        self._memory = memory
        self._prefix_messages = prefix_messages
        self._node_postprocessors = node_postprocessors or []
        self._context_template = context_template or DEFAULT_CONTEXT_TEMPLATE

    def _generate_context(self, message: str) -> Tuple[str, List[NodeWithScore]]:
        nodes = self._retriever.retrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(nodes, QueryBundle(message))
        context_str = "\n\n".join(
            [n.node.get_content(MetadataMode.LLM).strip() for n in nodes]
        )
        return self._context_template.format(context_str=context_str), nodes

    async def _agenerate_context(self, message: str) -> Tuple[str, List[NodeWithScore]]:
        nodes = await self._retriever.aretrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(nodes, QueryBundle(message))
        context_str = "\n\n".join(
            [n.node.get_content(MetadataMode.LLM).strip() for n in nodes]
        )
        return self._context_template.format(context_str=context_str), nodes

    def chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        context_str, nodes = self._generate_context(message)
        prefix_messages = [
            ChatMessage(content=context_str, role="system")
        ] + self._prefix_messages
        all_messages = prefix_messages + self._memory.get()
        chat_response = self._llm.chat(all_messages)
        ai_message = chat_response.message
        self._memory.put(ai_message)
        return AgentChatResponse(
            response=str(chat_response.message.content),
            sources=[ToolOutput(tool_name="retriever", content=context_str)],
            source_nodes=nodes,
        )

    async def achat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        if chat_history:
            self._memory.set(chat_history)
        self._memory.put(ChatMessage(content=message, role="user"))
        context_str, nodes = await self._agenerate_context(message)
        prefix_messages = [
            ChatMessage(content=context_str, role="system")
        ] + self._prefix_messages
        all_messages = prefix_messages + self._memory.get()
        chat_response = await self._llm.achat(all_messages)
        ai_message = chat_response.message
        self._memory.put(ai_message)
        return AgentChatResponse(
            response=str(chat_response.message.content),
            sources=[ToolOutput(tool_name="retriever", content=context_str)],
            source_nodes=nodes,
        )

    def reset(self) -> None:
        self._memory.reset()

    @property
    def chat_history(self) -> List[ChatMessage]:
        return self._memory.get_all()


class CondenseQuestionChatEngine(BaseChatEngine):
    """
    Condense Question Chat Engine.

    First generate a standalone question from conversation context and last message,
    then query the query engine for a response.
    """

    def __init__(
        self,
        query_engine: BaseQueryEngine,
        condense_question_prompt: PromptTemplate,
        memory: BaseMemory,
        llm: LLM,
        verbose: bool = False,
    ):
        self._query_engine = query_engine
        self._condense_question_prompt = condense_question_prompt
        self._memory = memory
        self._llm = llm
        self._verbose = verbose

    def _condense_question(
        self, chat_history: List[ChatMessage], last_message: str
    ) -> str:
        if not chat_history:
            return last_message
        chat_history_str = "\n".join([str(m) for m in chat_history])
        return self._llm.predict(
            self._condense_question_prompt,
            question=last_message,
            chat_history=chat_history_str,
        )

    async def _acondense_question(
        self, chat_history: List[ChatMessage], last_message: str
    ) -> str:
        if not chat_history:
            return last_message
        chat_history_str = "\n".join([str(m) for m in chat_history])
        return await self._llm.apredict(
            self._condense_question_prompt,
            question=last_message,
            chat_history=chat_history_str,
        )

    def chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        chat_history = chat_history or self._memory.get(input=message)
        condensed_question = self._condense_question(chat_history, message)
        query_response = self._query_engine.query(condensed_question)
        self._memory.put(ChatMessage(role="user", content=message))
        self._memory.put(ChatMessage(role="assistant", content=str(query_response)))
        return AgentChatResponse(
            response=str(query_response),
            sources=[ToolOutput(content=str(query_response), tool_name="query_engine")],
        )

    async def achat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentChatResponse:
        chat_history = chat_history or self._memory.get(input=message)
        condensed_question = await self._acondense_question(chat_history, message)
        query_response = await self._query_engine.aquery(condensed_question)
        self._memory.put(ChatMessage(role="user", content=message))
        self._memory.put(ChatMessage(role="assistant", content=str(query_response)))
        return AgentChatResponse(
            response=str(query_response),
            sources=[ToolOutput(content=str(query_response), tool_name="query_engine")],
        )

    def reset(self) -> None:
        self._memory.reset()

    @property
    def chat_history(self) -> List[ChatMessage]:
        return self._memory.get_all()
