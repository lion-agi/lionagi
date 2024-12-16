from typing import List

from pydantic import BaseModel, Field

from ..data_models import OpenAIEndpointResponseBody


class Categories(BaseModel):
    hate: bool = Field(
        description="Content that expresses, incites, or promotes hate based on race, gender, ethnicity, "
        "religion, nationality, sexual orientation, disability status, or caste. Hateful "
        "content aimed at non-protected groups (e.g., chess players) is harassment."
    )

    hate_threatening: bool = Field(
        alias="hate/threatening",
        description="Hateful content that also includes violence or serious harm towards the targeted "
        "group based on race, gender, ethnicity, religion, nationality, sexual orientation, "
        "disability status, or caste.",
    )

    harassment: bool = Field(
        description="Content that expresses, incites, or promotes harassing language towards any target."
    )

    harassment_threatening: bool = Field(
        alias="harassment/threatening",
        description="Harassment content that also includes violence or serious harm towards any target.",
    )

    self_harm: bool = Field(
        alias="self-harm",
        description="Content that promotes, encourages, or depicts acts of self-harm, such as suicide, "
        "cutting, and eating disorders.",
    )

    self_harm_intent: bool = Field(
        alias="self-harm/intent",
        description="Content where the speaker expresses that they are engaging or intend to engage in "
        "acts of self-harm, such as suicide, cutting, and eating disorders.",
    )

    self_harm_instructions: bool = Field(
        alias="self-harm/instructions",
        description="Content that encourages performing acts of self-harm, such as suicide, cutting, "
        "and eating disorders, or that gives instructions or advice on how to commit such acts.",
    )

    sexual: bool = Field(
        description="Content meant to arouse sexual excitement, such as the description of sexual activity, "
        "or that promotes sexual services (excluding sex education and wellness)."
    )

    sexual_minors: bool = Field(
        alias="sexual/minors",
        description="Sexual content that includes an individual who is under 18 years old.",
    )

    violence: bool = Field(
        description="Content that depicts death, violence, or physical injury."
    )

    violence_graphic: bool = Field(
        alias="violence/graphic",
        description="Content that depicts death, violence, or physical injury in graphic detail.",
    )


class CategoryScores(BaseModel):
    hate: float = Field(description="The score for the category 'hate'.")

    hate_threatening: float = Field(
        alias="hate/threatening",
        description="The score for the category 'hate/threatening'.",
    )

    harassment: float = Field(
        description="The score for the category 'harassment'."
    )

    harassment_threatening: float = Field(
        alias="harassment/threatening",
        description="The score for the category 'harassment/threatening'.",
    )

    self_harm: float = Field(
        alias="self-harm",
        description="The score for the category 'self-harm'.",
    )

    self_harm_intent: float = Field(
        alias="self-harm/intent",
        description="The score for the category 'self-harm/intent'.",
    )

    self_harm_instructions: float = Field(
        alias="self-harm/instructions",
        description="The score for the category 'self-harm/instructions'.",
    )

    sexual: float = Field(description="The score for the category 'sexual'.")

    sexual_minors: float = Field(
        alias="sexual/minors",
        description="The score for the category 'sexual/minors'.",
    )

    violence: float = Field(
        description="The score for the category 'violence'."
    )

    violence_graphic: float = Field(
        alias="violence/graphic",
        description="The score for the category 'violence/graphic'.",
    )


class Result(BaseModel):
    flagged: bool = Field(
        description="Whether the content violates OpenAI's usage policies."
    )

    categories: Categories = Field(
        description="A dictionary of per-category binary content policy violation flags.",
    )

    category_scores: CategoryScores = Field(
        description="A dictionary of per-category raw scores output by the model."
    )


class OpenAIModerationResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The unique identifier for the moderation request."
    )
    model: str = Field(
        description="The model used to generate the moderation results."
    )
    results: list[Result] = Field(description="A list of moderation objects.")
