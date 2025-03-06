from enum import Enum

from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    company = "company"
    research_paper = "research paper"
    news = "news"
    pdf = "pdf"
    github = "github"
    tweet = "tweet"
    personal_site = "personal site"
    linkedin_profile = "linkedin profile"
    financial_report = "financial report"


class LivecrawlEnum(str, Enum):
    never = "never"
    fallback = "fallback"
    always = "always"


class SearchTypeEnum(str, Enum):
    keyword = "keyword"
    neural = "neural"
    auto = "auto"


class ContentsText(BaseModel):
    includeHtmlTags: bool | None = Field(
        default=False,
        description="Whether to include HTML tags in the text. Set to True if you want to retain HTML structure for the LLM to interpret.",
    )
    maxCharacters: int | None = Field(
        default=None,
        description="The maximum number of characters to return from the webpage text.",
    )


class ContentsHighlights(BaseModel):
    highlightsPerUrl: int | None = Field(
        default=1,
        description="The number of highlight snippets you want per page.",
    )
    numSentences: int | None = Field(
        default=5,
        description="Number of sentences to return in each highlight snippet.",
    )
    query: None | str = Field(
        default=None,
        description="A specific query used to generate the highlight snippets.",
    )


class ContentsSummary(BaseModel):
    query: None | str = Field(
        default=None,
        description="A specific query used to generate a summary of the webpage.",
    )


class ContentsExtras(BaseModel):
    links: int | None = Field(
        default=None, description="Number of links to return from each page."
    )
    imageLinks: int | None = Field(
        default=None, description="Number of images to return for each result."
    )


class Contents(BaseModel):
    text: None | ContentsText = Field(
        default=None,
        description="Return full or partial text for each page, with optional HTML structure or size limit.",
    )
    highlights: None | ContentsHighlights = Field(
        default=None, description="Return snippet highlights for each page."
    )
    summary: None | ContentsSummary = Field(
        default=None, description="Return a short summary of each page."
    )
    livecrawl: None | LivecrawlEnum = Field(
        default=LivecrawlEnum.never,
        description="Livecrawling setting for each page. Options: never, fallback, always.",
    )
    livecrawlTimeout: int | None = Field(
        default=10000,
        description="Timeout in milliseconds for livecrawling. Default 10000.",
    )
    subpages: int | None = Field(
        default=None,
        description="Number of subpages to crawl within each URL.",
    )
    subpageTarget: None | str | list[str] = Field(
        default=None,
        description="A target subpage or multiple subpages (list) to crawl, e.g. 'cited papers'.",
    )
    extras: None | ContentsExtras = Field(
        default=None,
        description="Additional extras like links or images to return for each page.",
    )


class ExaSearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="The main query string describing what you're looking for.",
    )
    category: None | CategoryEnum = Field(
        default=None,
        description="A data category to focus on, such as 'company', 'research paper', 'news', etc.",
    )
    type: None | SearchTypeEnum = Field(
        default=None,
        description="The type of search to run. Can be 'auto', 'keyword', or 'neural'.",
    )
    useAutoprompt: None | bool = Field(
        default=False,
        description="If True, Exa auto-optimizes your query for best results (neural or auto search only).",
    )
    numResults: int | None = Field(
        default=10, description="Number of results to return. Default is 10."
    )
    includeDomains: None | list[str] = Field(
        default=None,
        description="List of domains you want to include exclusively.",
    )
    excludeDomains: None | list[str] = Field(
        default=None,
        description="List of domains you do NOT want to see in the results.",
    )
    startCrawlDate: None | str = Field(
        default=None,
        description="Include results crawled after this ISO date (e.g., '2023-01-01T00:00:00.000Z').",
    )
    endCrawlDate: None | str = Field(
        default=None,
        description="Include results crawled before this ISO date.",
    )
    startPublishedDate: None | str = Field(
        default=None,
        description="Only return results published after this ISO date.",
    )
    endPublishedDate: None | str = Field(
        default=None,
        description="Only return results published before this ISO date.",
    )
    includeText: None | list[str] = Field(
        default=None,
        description="Strings that must appear in the webpage text. Only a single string up to 5 words is currently supported.",
    )
    excludeText: None | list[str] = Field(
        default=None,
        description="Strings that must NOT appear in the webpage text. Only a single string up to 5 words is currently supported.",
    )
    contents: None | Contents = Field(
        default=None,
        description="Dict defining the different ways you want to retrieve webpage contents, including text, highlights, or summaries.",
    )
