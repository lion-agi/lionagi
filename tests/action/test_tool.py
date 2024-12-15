"""Tests for Tool implementation with real-world scenarios."""

import asyncio
import json
from collections.abc import Callable
from typing import Any

import pytest

from lionagi.action.tool import Tool
from lionagi.libs.async_utils import TCallParams


# Example tool functions that might be used in a real application
async def fetch_data(url: str, **kwargs: Any) -> dict[str, Any]:
    """Simulate fetching data from an API."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return {"url": url, "params": kwargs, "data": {"sample": "data"}}


async def process_text(
    text: str, language: str = "en", **kwargs: Any
) -> dict[str, Any]:
    """Simulate text processing operation."""
    return {
        "original": text,
        "language": language,
        "length": len(text),
        "processed": True,
    }


async def database_operation(
    query: str, params: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Simulate database operation."""
    if not query or not params:
        raise ValueError("Missing required parameters")
    return {"query": query, "params": params, "rows_affected": 1}


class TestTool:
    """Test Tool implementation with practical scenarios."""

    def test_tool_with_api_function(self) -> None:
        """Test tool wrapping an API function."""
        tool = Tool(
            function=fetch_data,
            schema_={
                "name": "fetch_data",
                "description": "Fetch data from an API endpoint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "format": "uri"},
                        "headers": {"type": "object"},
                    },
                    "required": ["url"],
                },
            },
        )

        assert tool.function == fetch_data
        assert tool.function_name == "fetch_data"
        assert "url" in tool.schema_["parameters"]["properties"]
        assert tool.tcall is not None
        assert not tool.tcall.timing

    def test_tool_with_text_processor(self) -> None:
        """Test tool wrapping a text processing function."""
        tool = Tool(
            function=process_text,
            schema_={
                "name": "process_text",
                "description": "Process text content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "language": {"type": "string", "default": "en"},
                    },
                    "required": ["text"],
                },
            },
        )

        assert tool.function == process_text
        assert "text" in tool.schema_["parameters"]["properties"]
        assert tool.schema_["parameters"]["required"] == ["text"]

    def test_tool_with_database_function(self) -> None:
        """Test tool wrapping a database operation."""
        tool = Tool(
            function=database_operation,
            schema_={
                "name": "database_operation",
                "description": "Execute database operation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "params": {"type": "object"},
                    },
                    "required": ["query", "params"],
                },
            },
        )

        assert tool.function == database_operation
        assert "query" in tool.schema_["parameters"]["properties"]
        assert "params" in tool.schema_["parameters"]["properties"]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_api_tool_execution(self) -> None:
        """Test executing an API tool."""
        tool = Tool(function=fetch_data)
        result = await tool.tcall.function(
            url="https://api.example.com/data",
            headers={"Authorization": "Bearer token"},
        )

        assert result["url"] == "https://api.example.com/data"
        assert "headers" in result["params"]
        assert "data" in result

    @pytest.mark.asyncio(loop_scope="function")
    async def test_text_processing_tool(self) -> None:
        """Test executing a text processing tool."""
        tool = Tool(function=process_text)
        result = await tool.tcall.function(text="Hello, world!", language="en")

        assert result["original"] == "Hello, world!"
        assert result["language"] == "en"
        assert result["length"] == len("Hello, world!")
        assert result["processed"]

    @pytest.mark.asyncio
    async def test_database_tool_error(self) -> None:
        """Test database tool error handling."""
        tool = Tool(function=database_operation)

        with pytest.raises(ValueError):
            await tool.tcall.function(query="", params={})

    def test_tool_schema_generation(self) -> None:
        """Test automatic schema generation from function."""
        tool = Tool(function=process_text)
        schema = tool.schema_

        assert schema["name"] == "process_text"
        assert "parameters" in schema
        assert "text" in schema["parameters"]["properties"]
        assert "language" in schema["parameters"]["properties"]

    def test_tool_with_custom_tcall(self) -> None:
        """Test tool with custom TCallParams."""
        custom_tcall = TCallParams()
        tool = Tool(function=fetch_data, tcall=custom_tcall)

        assert tool.tcall is not None
        assert tool.tcall.function == fetch_data
        assert not tool.tcall.timing

    def test_tool_string_representation(self) -> None:
        """Test string representation of tool."""
        tool = Tool(function=fetch_data)
        expected = "Tool(name=fetch_data)"
        assert str(tool) == expected

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self) -> None:
        """Test concurrent execution of tools."""
        api_tool = Tool(function=fetch_data)
        text_tool = Tool(function=process_text)

        results = await asyncio.gather(
            api_tool.tcall.function(url="https://api.example.com"),
            text_tool.tcall.function(text="Test text"),
        )

        assert len(results) == 2
        assert "url" in results[0]
        assert "original" in results[1]
