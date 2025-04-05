from pydantic import Field

from lionagi.models import HashableModel

from .base import CodeSnippet, TextSnippet

__all__ = (
    "ResearchFinding",
    "PotentialRisk",
    "ResearchSummary",
)


class ResearchFinding(HashableModel):
    """
    A single piece of information or insight from the research phase.
    """

    summary: str | None = Field(
        None,
        description="Concise text describing the discovered fact, concept, or best practice.",
    )
    snippets: list[TextSnippet | CodeSnippet] = Field(
        default_factory=list,
        description="Ordered list of content snippets (text or code) that illustrate or support the finding.",
    )
    relevance: str | None = Field(
        default=None,
        description="Why this finding matters to the project. E.g., 'Helps solve concurrency issue.'",
    )


class PotentialRisk(HashableModel):
    """
    Identifies a risk or challenge discovered during research.
    """

    description: str | None = Field(
        None,
        description="Short text describing the risk. E.g., 'Scalability concerns with chosen DB'.",
    )
    impact: str | None = Field(
        default=None,
        description="Possible consequences if not mitigated. E.g., 'System slowdown, possible downtime.'",
    )
    mitigation_ideas: str | None = Field(
        default=None,
        description="Preliminary ways to reduce or handle this risk.",
    )
