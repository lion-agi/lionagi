from abc import ABC


class PileQueryMixin(ABC):

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

        from lionagi.os.core.action.tool_manager import func_to_tool

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

    # def create_index(self, index_type="llama_index", **kwargs):
    #     """
    #     Create an index for the pile.

    #     Args:
    #         index_type (str): The type of index to use. Default is "llama_index".
    #         **kwargs: Additional keyword arguments for the index creation.

    #     Returns:
    #         The created index.

    #     Raises:
    #         ValueError: If an invalid index type is provided.
    #     """
    #     if index_type == "llama_index":
    #         from lionagi.integrations.bridge import LlamaIndexBridge

    #         index_nodes = None

    #         try:
    #             index_nodes = [i.to_llama_index_node() for i in self]
    #         except AttributeError:
    #             raise LionTypeError(
    #                 "Invalid item type. Expected a subclass of Component."
    #             )

    #         self.index = LlamaIndexBridge.index(index_nodes, **kwargs)
    #         return self.index

    #     raise ValueError("Invalid index type")
