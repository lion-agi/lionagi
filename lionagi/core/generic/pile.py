from collections.abc import Iterable
from typing import TypeVar, Type, Any

from pydantic import Field
import lionagi.libs.lionfuncs as ln
from lion_core.exceptions import LionTypeError, LionResourceError


from lion_core.generic.pile import Pile as CorePile
from lionagi.core.generic.component import Component


T = TypeVar("T")


class Pile(CorePile):
    use_obj: bool = False
    name: str | None = None
    index: Any = None
    engines: dict[str, Any] = Field(default_factory=dict)
    query_response: list = []
    tools: dict = {}

    def to_df(self):
        """Return the pile as a DataFrame."""
        dicts_ = []
        for i in self:
            _dict = ln.to_dict(i)
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return ln.to_df(dicts_)

    def create_index(self, index_type="llama_index", **kwargs):
        """
        Create an index for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            **kwargs: Additional keyword arguments for the index creation.

        Returns:
            The created index.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            from lionagi.integrations.bridge import LlamaIndexBridge

            index_nodes = None

            try:
                index_nodes = [i.to_llama_index_node() for i in self]
            except AttributeError:
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

            self.index = LlamaIndexBridge.index(index_nodes, **kwargs)
            return self.index

        raise ValueError("Invalid index type")

    def create_query_engine(self, index_type="llama_index", engine_kwargs={}, **kwargs):
        """
        Create a query engine for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the index creation.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            if "node_postprocessor" in kwargs:
                engine_kwargs["node_postprocessor"] = kwargs.pop("node_postprocessor")
            if "llm" in kwargs:
                engine_kwargs["llm"] = kwargs.pop("llm")
            if not self.index:
                self.create_index(index_type, **kwargs)
            query_engine = self.index.as_query_engine(**engine_kwargs)
            self.engines["query"] = query_engine
        else:
            raise ValueError("Invalid index type")

    def create_chat_engine(self, index_type="llama_index", engine_kwargs={}, **kwargs):
        """
        Create a chat engine for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the index creation.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            if "node_postprocessor" in kwargs:
                engine_kwargs["node_postprocessor"] = kwargs.pop("node_postprocessor")
            if "llm" in kwargs:
                engine_kwargs["llm"] = kwargs.pop("llm")
            if not self.index:
                self.create_index(index_type, **kwargs)
            query_engine = self.index.as_chat_engine(**engine_kwargs)
            self.engines["chat"] = query_engine
        else:
            raise ValueError("Invalid index type")

    async def query_pile(self, query, engine_kwargs={}, **kwargs):
        """
        Query the pile using the created query engine.

        Args:
            query (str): The query to send.
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the query.

        Returns:
            str: The response from the query engine.
        """
        if not self.engines.get("query", None):
            self.create_query_engine(**engine_kwargs)
        response = await self.engines["query"].aquery(query, **kwargs)
        self.query_response.append(response)
        return str(response)

    async def chat_pile(self, query, engine_kwargs={}, **kwargs):
        """
        Chat with the pile using the created chat engine.

        Args:
            query (str): The query to send.
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the query.

        Returns:
            str: The response from the chat engine.
        """
        if not self.engines.get("chat", None):
            self.create_chat_engine(**engine_kwargs)
        response = await self.engines["chat"].achat(query, **kwargs)
        self.query_response.append(response)
        return str(response)

    async def embed_pile(
        self, imodel=None, field="content", embed_kwargs={}, verbose=True, **kwargs
    ):
        """
        Embed the items in the pile.

        Args:
            imodel: The embedding model to use.
            field (str): The field to embed. Default is "content".
            embed_kwargs (dict): Additional keyword arguments for the embedding.
            verbose (bool): Whether to print verbose messages. Default is True.
            **kwargs: Additional keyword arguments for the embedding.

        Raises:
            ModelLimitExceededError: If the model limit is exceeded.
        """
        from .model import iModel

        imodel = imodel or iModel(endpoint="embeddings", **kwargs)

        max_concurrency = kwargs.get("max_concurrency", None) or 100

        @ln.CallDecorator.max_concurrency(max_concurrency)
        async def _embed_item(item):
            try:
                return await imodel.embed_node(item, field=field, **embed_kwargs)
            except LionResourceError:
                pass
            return None

        await ln.alcall(list(self), _embed_item)

        a = len([i for i in self if "embedding" in i._all_fields])
        if len(self) > a and verbose:
            print(
                f"Successfully embedded {a}/{len(self)} items, Failed to embed {len(self) - a}/{len(self)} items"
            )
            return

        print(f"Successfully embedded all {a}/{a} items")

    def to_csv(self, file_name, **kwargs):
        """
        Save the pile to a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV writer.
        """
        self.to_df().to_csv(file_name, index=False, **kwargs)

    @classmethod
    def from_csv(cls, file_name, **kwargs):
        """
        Load a pile from a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV reader.

        Returns:
            Pile: The loaded pile.
        """
        from pandas import read_csv

        df = read_csv(file_name, **kwargs)
        items = Component.from_obj(df)
        return cls(items)

    @classmethod
    def from_df(cls, df):
        """
        Load a pile from a DataFrame.

        Args:
            df (DataFrame): The DataFrame to load.

        Returns:
            Pile: The loaded pile.
        """
        items = Component.from_obj(df)
        return cls(items)

    def as_query_tool(
        self,
        index_type="llama_index",
        query_type="query",
        name=None,
        guidance=None,
        query_description=None,
        **kwargs,
    ):
        """
        Create a query tool for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            query_type (str): The type of query engine to use. Default is "query".
            name (str): The name of the query tool. Default is "query".
            guidance (str): The guidance for the query tool.
            query_description (str): The description of the query parameter.
            **kwargs: Additional keyword arguments for the query engine.

        Returns:
            Tool: The created query tool.
        """
        if not self.engines.get(query_type, None):
            if query_type == "query":
                self.create_query_engine(index_type=index_type, **kwargs)
            elif query_type == "chat":
                self.create_chat_engine(index_type=index_type, **kwargs)

        from lionagi.core.action.tool_manager import func_to_tool

        if not guidance:
            if query_type == "query":
                guidance = "Query a QA bot"
            elif query_type == "chat":
                guidance = "Chat with a QA bot"

        if not query_description:
            if query_type == "query":
                query_description = "The query to send"
            elif query_type == "chat":
                query_description = "The message to send"

        async def query(query: str):
            if query_type == "query":
                return await self.query_pile(query, **kwargs)

            elif query_type == "chat":
                return await self.chat_pile(query, **kwargs)

        name = name or "query"
        tool = func_to_tool(query)[0]
        tool.schema_["function"]["name"] = name
        tool.schema_["function"]["description"] = guidance
        tool.schema_["function"]["parameters"]["properties"]["query"][
            "description"
        ] = query_description
        self.tools[query_type] = tool
        return self.tools[query_type]

    def __str__(self):
        """
        Get the string representation of the pile.

        Returns:
            str: The string representation of the pile.
        """
        return self.to_df().__str__()

    def __repr__(self):
        """
        Get the representation of the pile.

        Returns:
            str: The representation of the pile.
        """
        return self.to_df().__repr__()


def pile(
    items: Iterable[T] | None = None,
    item_type: set[Type] | None = None,
    order=None,
    use_obj=None,
    csv_file=None,
    df=None,
    **kwargs,
) -> Pile[T]:
    """
    Create a new Pile instance.

    This function provides various ways to create a Pile instance:
    - Directly from items
    - From a CSV file
    - From a DataFrame

    Args:
        items (Iterable[T] | None): The items to include in the pile.
        item_type (set[Type] | None): The allowed types of items in the pile.
        order (list[str] | None): The order of items.
        use_obj (bool | None): Whether to treat Record and Ordering as objects.
        csv_file (str | None): The path to a CSV file to load items from.
        df (DataFrame | None): A DataFrame to load items from.
        **kwargs: Additional keyword arguments for loading from CSV or DataFrame.

    Returns:
        Pile[T]: A new Pile instance.

    Raises:
        ValueError: If invalid arguments are provided.
    """
    if csv_file:
        return Pile.from_csv(csv_file, **kwargs)
    if df:
        return Pile.from_df(df)

    return Pile(items, item_type, order, use_obj)
