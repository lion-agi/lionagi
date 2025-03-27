from pathlib import Path

from pydantic import Field, field_validator

from .base import HashableModel, Source

__all__ = (
    "File",
    "CodeFile",
    "Documentation",
)


class File(HashableModel):
    """
    Represents a generic file with an optional name, content, and brief
    description. Useful for capturing and validating metadata about any
    kind of file within a project.
    """

    file_name: str | None = Field(
        default=None,
        description=(
            "Provide the name of the file or its relative path in the "
            "project. If an absolute path is given, it will be converted"
            " to a string. "
        ),
        examples=[
            "session.py",
            "src/components/UserCard.tsx",
            "/absolute/path/to/my_file.txt",
        ],
    )
    content: str | None = Field(
        default=None,
        description=(
            "Paste or generate the full textual content of the file here. "
            "For example, this might include plain text, Markdown, or any "
            "other text format.\nExamples:\n"
            "  - '# My Title\\nSome description...'\n"
            "  - 'function greet() { return \"Hello\"; }'"
        ),
    )
    description: str | None = Field(
        default=None,
        description=(
            "Briefly explain the file's purpose or function within the "
            "project. This can be a short summary describing why this "
            "file is needed and/or what it does."
        ),
        examples=[
            "Manages user session logic for the LionAGI framework.",
            "Contains CSS styles for the navbar component.",
        ],
    )

    @field_validator("file_name", mode="before")
    def validate_file_name(cls, value):
        if isinstance(value, Path):
            return str(value)
        return value

    def render_content(
        self,
        header: str | None = None,
        footer: str | None = None,
    ) -> str:
        text = f"\n{header}\n\n" if header else ""
        text += self.content if self.content else ""
        if not footer:
            return text
        return text + f"\n\n{footer}\n"

    def persist(
        self,
        directory: Path | str,
        overwrite: bool = True,
        timestamp: bool = False,
        random_hash_digits: int = None,
        header: str | None = None,
        footer: str | None = None,
    ) -> Path:
        from lionagi.utils import create_path

        fp = create_path(
            directory=directory,
            filename=self.file_name,
            file_exist_ok=overwrite,
            timestamp=timestamp,
            random_hash_digits=random_hash_digits,
        )
        fp.write_text(self.render_content(header=header, footer=footer))
        return fp


class CodeFile(File):
    """
    Represents a code file with an identifiable programming language. Inherits
    from the generic File model but specializes for code-related content.
    """

    language: str | None = Field(
        default=None,
        description=(
            "Indicate the programming language of this code file. "
            "LLMs or humans can use this info to apply specific formatting or syntax analysis."
        ),
        examples=[
            "python",
            "json",
            "typescript",
            "html",
            "css",
            "java",
            "cpp",
        ],
    )
    content: str | None = Field(
        default=None,
        description=(
            "Provide or generate the **full source code**. This should be the primary text content "
            "of the code file, including all function/class definitions.\nNo md codeblock, only raw code"
        ),
        examples=[
            'def my_function():\\n    print("Hello, world!")',
            'export function greet(): string { return "Hello"; }',
        ],
    )


class Documentation(File):
    """
    Represents a documentation file, typically Markdown-based, that includes
    a title and main content explaining or describing some aspect of the project.
    """

    title: str = Field(
        default_factory=str,
        description=(
            "Specify the title of this documentation entry or page. "
            "For instance, this might be the top-level heading in a Markdown file.\n"
        ),
        examples=["Getting Started", "API Reference: LionAGI Session Module"],
    )
    content: str = Field(
        default_factory=str,
        description=(
            "Provide the primary Markdown (or similar) content for the documentation. "
            "This can include headings, bullet points, tables, code snippets, etc.\n"
        ),
    )
    sources: list[Source] | None = Field(
        default=None,
        description=(
            "List of sources or references used to create this documentation. "
            "Each source should include a title and URL to the original content."
        ),
    )

    def render_content(
        self,
        header: str | None = None,
        footer: str | None = None,
        include_source: bool = False,
    ) -> str:
        """
        Renders the documentation content, optionally including citations for sources.
        """
        footer = footer or ""
        if include_source and self.sources:
            footer = "\n\n## Sources\n"
            for source in self.sources:
                footer += f"- [{source.title}]({source.url})\n"
                footer += f"  - {source.note}\n" if source.note else ""
        return super().render_content(header=header, footer=footer)


# File: lionagi/fields/file.py
