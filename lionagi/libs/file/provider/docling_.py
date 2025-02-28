# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path

# TODO: finish docling provider, potentially formalize provider interface


class DoclingProvider:

    def __init__(
        self,
        allowed_formats: list[str] = None,
        format_options: dict = None,
    ):
        from docling.document_converter import DocumentConverter

        from lionagi.libs.package.imports import check_import

        DocumentConverter = check_import(
            "docling",
            module_name="document_converter",
            import_name="DocumentConverter",
        )
        self.converter = DocumentConverter(
            allowed_formats=allowed_formats, format_options=format_options
        )
        self.reader_tool = lambda x: self.converter.convert(
            x
        ).document.export_to_markdown()

    def read_url_or_path(
        self,
        url_or_path: Path | str,
    ): ...

    ...
