from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from lionagi.models import FieldModel


class File(BaseModel):
    """
    Represents a generic file with an optional name, content, and brief description.
    Useful for capturing and validating metadata about any kind of file within a project.
    """

    file_name: str | None = Field(
        default=None,
        description=(
            "Provide the name of the file or its relative path in the project. "
            "If an absolute path is given, it will be converted to a string. "
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
            "For example, this might include plain text, Markdown, or any other text format.\n"
            "Examples:\n"
            "  - '# My Title\\nSome description...'\n"
            "  - 'function greet() { return \"Hello\"; }'"
        ),
    )
    description: str | None = Field(
        default=None,
        description=(
            "Briefly explain the file's purpose or function within the project. "
            "This can be a short summary describing why this file exists or what it does.\n"
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
            "of the code file, including all function/class definitions.\n"
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
        examples=[
            "# Getting Started\\nThis guide walks you through ...",
            "# API Reference\\n## Session Class\\n...",
        ],
    )


FILE_FIELD = FieldModel(
    name="file",
    annotation=File | None,
    default=None,
)

CODE_FILE_FIELD = FieldModel(
    name="code_file",
    annotation=CodeFile | None,
    default=None,
)

DOCUMENTATION_FIELD = FieldModel(
    name="documentation",
    annotation=Documentation | None,
    default=None,
)

# File: lionagi/libs/fields/file.py
