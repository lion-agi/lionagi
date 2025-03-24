from enum import Enum

from pydantic import Field, HttpUrl

from lionagi.models import HashableModel

__all__ = (
    "Source",
    "TextSnippet",
    "CodeSnippet",
    "Section",
    "OutlineItem",
    "Outline",
)


class Source(HashableModel):
    """
    Represents a citation or external source, such as:
     - a website,
     - documentation link,
     - research paper,
     - or any external resource.
    """

    title: str = Field(
        ...,
        description="Short label or title for the reference (e.g. 'Pydantic Docs', 'RFC 3986').",
    )

    url: str | HttpUrl | None = Field(
        None,
        description="Full URL or local path pointing to the resource. Must conform to standard URL format.",
    )

    note: str | None = Field(
        default=None,
        description=(
            "Optional additional note explaining why this reference is relevant or what it contains."
        ),
    )


class SnippetType(str, Enum):
    TEXT = "text"
    CODE = "code"


class TextSnippet(HashableModel):
    """
    Specialized snippet for textual/prose content.
    """

    type: SnippetType = Field(
        SnippetType.TEXT,
        description=(
            "Must be 'text' for textual snippets. Ensures explicit type distinction."
        ),
    )
    content: str = Field(
        ...,
        description=(
            "The actual text. Can be a paragraph, bullet list, or any narrative content."
        ),
    )


class CodeSnippet(HashableModel):
    """
    Specialized snippet for source code or command-line examples.
    """

    type: SnippetType = Field(
        SnippetType.CODE,
        description=(
            "Must be 'code' for code snippets. Allows separate handling or formatting."
        ),
    )
    content: str = Field(
        ...,
        description=(
            "The actual code or command sequence. Should be well-formatted so it can be rendered properly."
        ),
    )


class Section(HashableModel):
    """
    A single section of a document or article. Each section has:
     - A title
     - A sequential list of content snippets (text or code),
       which appear in the intended reading order.
     - Optional sources specifically cited in this section.
    """

    title: str = Field(
        ...,
        description=(
            "The section heading or label, e.g., 'Introduction', 'Implementation Steps'."
        ),
    )
    snippets: list[TextSnippet | CodeSnippet] = Field(
        default_factory=list,
        description=(
            "Ordered list of content snippets. Could be multiple text blocks, code examples, etc."
        ),
    )

    sources: list[Source] = Field(
        default_factory=list,
        description=(
            "References specifically cited in this section. "
            "If sources are stored at the doc-level, this can be omitted."
        ),
    )


class OutlineItem(HashableModel):
    """
    Represents a single outline item, which could become a full section later.
    """

    heading: str = Field(
        ...,
        description="Short name or label for this item, e.g., 'Chapter 1: Basics'.",
    )
    summary: str | None = Field(
        default=None,
        description=(
            "A brief description of what this section will cover, if known."
        ),
    )


class Outline(HashableModel):
    """
    A top-level outline for a document or article.
    Usually used in early planning stages.
    """

    topic: str = Field(
        ..., description="Working title or overarching topic of the document."
    )
    items: list[OutlineItem] = Field(
        default_factory=list,
        description="List of major outline points or sections planned.",
    )
    notes: str | None = Field(
        default=None,
        description="Any additional remarks, questions, or brainstorming notes for the outline.",
    )
