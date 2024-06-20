from lionagi.services.api.util import get_url_content, get_url_response
import os
from typing import Dict, Any, List

google_key_scheme = "GOOGLE_API_KEY"
google_engine_scheme = "GOOGLE_CSE_ID"

google_api_key = os.getenv(google_key_scheme)
google_engine = os.getenv(google_engine_scheme)


class GoogleSearch:
    """
    A utility class for performing Google searches and retrieving search results.

    Attributes:
        api_key (str): The Google API key used for search (can be set via
                       environment variable).
        search_engine (str): The Google Custom Search Engine ID (can be set
                             via environment variable).

    Methods:
        search(query: str = None, url: str = None) -> List[Dict[str, Any]]:
            Perform a Google search for a given query or URL and retrieve
            relevant content.
    """

    api_key = google_api_key
    search_engine = google_engine
    search_url = """
        https://www.googleapis.com/customsearch/v1?key={key}&cx={engine}&q={query}&start={start}
    """

    @classmethod
    def create_agent(cls, api_key=None, search_engine=None, verbose=False):
        """
        Create an OpenAIAgent for Google search operations.

        Args:
            api_key (str, optional): The Google API key for search. Defaults to None (uses class attribute).
            search_engine (str, optional): The Google Custom Search Engine ID. Defaults to None (uses class attribute).
            verbose (bool, optional): Whether to enable verbose mode for the agent. Defaults to False.

        Returns:
            OpenAIAgent: An instance of the OpenAIAgent for performing Google searches.

        Raises:
            ImportError: If there is an issue during the agent creation.
        """
        try:
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
                module_name="tools.google",
                import_name="GoogleSearchToolSpec",
                pip_name="llama-index-tools-google",
            )

            from llama_index.agent.openai import OpenAIAgent
            from llama_index.core.tools.tool_spec.load_and_search.base import (
                LoadAndSearchToolSpec,
            )
            from llama_index.tools.google import GoogleSearchToolSpec
            from llama_index.llms.openai import OpenAI

            llm = OpenAI(model="gpt-4-turbo", temperature=0.1)

            api_key = api_key if api_key else cls.api_key
            search_engine = search_engine if search_engine else cls.search_engine
            google_spec = GoogleSearchToolSpec(key=api_key, engine=search_engine)

            # Wrap the google search tool as it returns large payloads
            tools = LoadAndSearchToolSpec.from_defaults(
                google_spec.to_tool_list()[0],
            ).to_tool_list()

            # Create the Agent with our tools
            agent = OpenAIAgent.from_tools(tools, verbose=verbose, llm=llm)
            return agent

        except Exception as e:
            raise ImportError(f"Error in importing OpenAIAgent from llama_index: {e}")

    @classmethod
    async def _get_search_item_field(cls, item: Dict[str, Any]) -> Dict[str, str]:
        """
        Extracts relevant fields from a search item.

        Args:
            item (Dict[str, Any]): The search item.

        Returns:
            Dict[str, str]: A dictionary containing relevant fields.
        """
        try:
            long_description = item["pagemap"]["metatags"][0].get(
                "og:description", "N/A"
            )
        except KeyError:
            long_description = "N/A"

        url = item.get("link")
        content = await get_url_content(url) if url else "N/A"
        return {
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": url,
            "long_description": long_description,
            "content": content,
        }

    @classmethod
    def _format_search_url(
        cls, url: str, api_key: str, search_engine: str, query: str, start: int
    ) -> str:
        """
        Format the search URL with the given parameters.

        Args:
            url (str): The base URL for the search.
            api_key (str): The Google API key.
            search_engine (str): The Google Custom Search Engine ID.
            query (str): The search query.
            start (int): The starting index for search results.

        Returns:
            str: The formatted search URL.
        """
        url = url or cls.search_url
        return url.format(
            key=api_key or cls.api_key,
            engine=search_engine or cls.search_engine,
            query=query,
            start=start,
        )

    @classmethod
    async def search(
        cls,
        query: str = None,
        url: str = None,
        search_url: str = None,
        api_key: str = None,
        search_engine: str = None,
        start: int = 1,
        timeout: tuple = (0.5, 0.5),
        content: bool = True,
        num: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform a Google search for a given query or URL and retrieve relevant
        content.

        Args:
            query (str, optional): The search query. Defaults to None.
            url (str, optional): The URL to retrieve content from. Defaults
                                 to None.
            search_url (str, optional): The search URL template. Defaults
                                        to None.
            api_key (str, optional): The Google API key. Defaults to None.
            search_engine (str, optional): The Google Custom Search Engine ID.
                                           Defaults to None.
            start (int, optional): The starting index for search results.
                                   Defaults to 1.
            timeout (tuple, optional): The timeout for the request. Defaults
                                       to (0.5, 0.5).
            content (bool, optional): Whether to include content in the
                                      results. Defaults to True.
            num (int, optional): The number of search results to retrieve.
                                 Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of search results with relevant
                                  fields.

        Raises:
            ValueError: If both query and URL are None.
        """
        if not query and not url:
            raise ValueError("No search input.")

        if url:
            return [await get_url_content(url)]
        else:
            formatted_url = cls._format_search_url(
                url=search_url,
                query=query,
                api_key=api_key,
                search_engine=search_engine,
                start=start,
            )
            response = await get_url_response(formatted_url, timeout=timeout)
            response_dict = response.json()
            items = response_dict.get("items", [])[:num]
            if content:
                items = [await cls._get_search_item_field(item) for item in items]
            return items

    async def query(query): ...
