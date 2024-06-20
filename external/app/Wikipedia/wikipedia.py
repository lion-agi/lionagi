class WikipediaSearch:
    """
    A utility class for searching and retrieving information from Wikipedia.
    Methods:
        query(query: str, lang: str = 'en'):
            Search for a query on Wikipedia and retrieve relevant information.
    """

    # @staticmethod
    def create_agent(verbose=False):
        from lionagi.os.lib.sys_util import check_import

        check_import(package_name="llama_index", pip_name="llama-index")

        check_import(
            package_name="llama_index",
            module_name="agent.openai",
            import_name="OpenAIAgent",
            pip_name="llama-index-agent-openai",
        )

        check_import(
            package_name="llama_index",
            module_name="tools.wikipedia",
            import_name="WikipediaToolSpec",
            pip_name="llama-index-tools-wikipedia",
        )

        from llama_index.tools.wikipedia import WikipediaToolSpec
        from llama_index.agent.openai import OpenAIAgent
        from llama_index.llms.openai import OpenAI

        llm = OpenAI(model="gpt-4o", temperature=0.1)

        tool_spec = WikipediaToolSpec()

        agent = OpenAIAgent.from_tools(
            tool_spec.to_tool_list(), verbose=verbose, llm=llm
        )
        return agent

    async def query(query): ...
