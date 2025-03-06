# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from lionagi.tools.base import Provider
from lionagi.operatives.action.tool import Tool

DOCLING_INPUT_FORMATS = {
    "pdf",
    "docx",
    "xlsx",
    "pptx",
    "md",
    "html",
    "xhtml",
    "csv",
    "png",
    "jpeg",
    "tiff",
    "bmp",
}


class DoclingProvider(Provider):
    
    name: str = "docling"
    capabilities: tuple[str] = ("read", "chunk", "convert")
    
    
    def __init__(self):
        from lionagi.libs.package.imports import check_import

        DocumentConverter = check_import(
            "docling",
            module_name="document_converter",
            import_name="DocumentConverter",
        )
        
        self.converter = DocumentConverter()
        self.tools = {}

    def _create_tool(self, capability: str, **kwargs) -> Tool:
        if capability in self.tools:
            return self.tools[capability]
        if capability == "read":
            return self._create_read_tool(**kwargs)
        if capability == "chunk":
            return self._create_chunk_tool(**kwargs)
        if capability == "convert":
            return self._create_convert_tool(**kwargs)
        
    def _create_read_tool(self, **kwargs) -> Tool:
        ...

    def _create_chunk_tool(self, **kwargs) -> Tool:
        ...
        
    def _create_convert_tool(self, **kwargs) -> Tool:
        ...


