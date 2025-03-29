from abc import abstractmethod
from pathlib import Path

from pydantic import Field, field_validator

from .base import HashableModel, Source
from .code import Class, Function, Import
from .research import PotentialRisk, ResearchFinding

__all__ = (
    "File",
    "Documentation",
    "ResearchSummary",
    "Module",
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

    @abstractmethod
    def render_content(
        self,
        header: str | None = None,
        footer: str | None = None,
    ) -> str:
        pass

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
        include_source: bool = True,
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
        return (header or "") + self.content + footer


class ResearchSummary(Documentation):
    """
    Captures the final outcome of the deep research process.
    """

    scope: str | None = Field(
        default=None,
        description="Brief statement of what was investigated. E.g., 'Surveyed python-based ORMs.'",
    )
    main_takeaways: str = Field(
        ...,
        description="High-level summary of the most critical insights for the project.",
    )
    findings: list[ResearchFinding] = Field(
        default_factory=list,
        description="List of key facts or knowledge gained.",
    )
    risks: list[PotentialRisk] = Field(
        default_factory=list,
        description="Identified obstacles or concerns for the project.",
    )

    def render_content(
        self,
        header: str | None = None,
        footer: str | None = None,
    ) -> str:
        """
        Renders the documentation content, optionally including citations for sources.
        """
        content = self.model_dump(exclude_unset=True, exclude_none=True)

        from lionagi.libs.schema.as_readable import as_readable

        text = as_readable(content, md=True, format_curly=True)

        footer = footer or ""
        if self.sources:
            footer = "\n\n## Sources\n"
            for source in self.sources:
                footer += f"- [{source.title}]({source.url})\n"
                footer += f"  - {source.note}\n" if source.note else ""
        return (header or "") + text + footer


class Module(File):
    """
    Represents a single source file: docstring, imports, top-level functions, classes, etc.
    """

    name: str = Field(
        ...,
        description="Logical name for this file/module (e.g., 'utils', 'main', 'data_models').",
    )
    path: str | None = Field(
        default=None,
        description="Filesystem path if known (e.g., 'src/utils.py').",
    )
    docstring: str | None = Field(
        default=None, description="File-level docstring or comments if any."
    )
    imports: list[Import] = Field(
        default_factory=list,
        description="All import statements / using directives / includes in this file.",
    )
    classes: list[Class] = Field(
        default_factory=list,
        description="All class or interface definitions in this file.",
    )
    functions: list[Function] = Field(
        default_factory=list,
        description="All top-level (non-class) functions in this file.",
    )
    variables: list = Field(
        default_factory=list,
        description="All top-level variables/constants in this file.",
    )
    language: str = Field(
        default_factory=str,
        description=(
            "Indicate the programming language of this code file. e.g., 'python', 'typescript'. "
            "LLMs or humans can use this info to apply specific formatting or syntax analysis."
        ),
    )

    def render_content(
        self,
        header: str | None = None,
        footer: str | None = None,
    ) -> str:
        """
        Renders the documentation content, optionally including citations for sources.
        """
        text = self.model_dump_json(exclude_none=True, exclude_unset=True)
        return header or "" + text + footer or ""


# File: lionagi/fields/file.py
