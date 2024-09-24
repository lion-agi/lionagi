from typing import Callable, Type, Any
from lionagi.core.generic.pile import Pile
from lionagi.core.generic.node import Node


class LangChainBridge:

    from .utils import LC_META_FIELDS

    meta_fields = LC_META_FIELDS

    @staticmethod
    def chunk(
        data: str | list[str],
        splitter: str | Callable,
        /,
        *splitter_args,
        **splitter_kwargs,
    ) -> list[str]:
        """uses langchain text_splitter"""
        from .chunker import langchain_text_splitter

        return langchain_text_splitter(
            data=data,
            splitter=splitter,
            *splitter_args,
            **splitter_kwargs,
        )

    @staticmethod
    def converter() -> Type:
        from .converter import LangChainConverter

        return LangChainConverter

    @staticmethod
    def load_file(loader, /, *args, **kwargs) -> Any:
        from .loader import langchain_loader

        return langchain_loader(loader, *args, **kwargs)

    @staticmethod
    def read_file(reader: str | Callable, /, *args, **kwargs) -> Pile[Node]:
        from .loader import langchain_reader

        return langchain_reader(reader, *args, **kwargs)

    @staticmethod
    def to_langchain(**kwargs):
        from .converter import LangChainConverter

        return LangChainConverter.to_obj(**kwargs)

    # backwards compatibility
    @staticmethod
    def to_langchain_document(*args, **kwargs):
        return LangChainBridge.to_langchain_document(*args, **kwargs)
