from typing import List, Union, Dict
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ModerationModel(str, Enum):
    LATEST = "text-moderation-latest"
    STABLE = "text-moderation-stable"


class ModerationCategories(BaseModel):
    sexual: bool = Field(
        ..., description="Content that refers to sexual activity or behavior."
    )
    hate: bool = Field(..., description="Hateful or discriminatory content.")
    harassment: bool = Field(
        ..., description="Content that harasses or intimidates individuals or groups."
    )
    self_harm: bool = Field(..., description="Content related to self-harm or suicide.")
    sexual_minors: bool = Field(
        ..., alias="sexual/minors", description="Sexual content involving minors."
    )
    hate_threatening: bool = Field(
        ...,
        alias="hate/threatening",
        description="Hateful content that is also threatening.",
    )
    violence_graphic: bool = Field(
        ..., alias="violence/graphic", description="Graphic violence or gore."
    )
    self_harm_intent: bool = Field(
        ...,
        alias="self-harm/intent",
        description="Content expressing intent to self-harm.",
    )
    self_harm_instructions: bool = Field(
        ..., alias="self-harm/instructions", description="Instructions for self-harm."
    )
    harassment_threatening: bool = Field(
        ...,
        alias="harassment/threatening",
        description="Harassment that is also threatening.",
    )
    violence: bool = Field(..., description="Violent content or threats of violence.")


class ModerationCategoryScores(BaseModel):
    sexual: float
    hate: float
    harassment: float
    self_harm: float
    sexual_minors: float = Field(..., alias="sexual/minors")
    hate_threatening: float = Field(..., alias="hate/threatening")
    violence_graphic: float = Field(..., alias="violence/graphic")
    self_harm_intent: float = Field(..., alias="self-harm/intent")
    self_harm_instructions: float = Field(..., alias="self-harm/instructions")
    harassment_threatening: float = Field(..., alias="harassment/threatening")
    violence: float


class ModerationResult(BaseModel):
    flagged: bool = Field(
        ..., description="Whether the content violates OpenAI's usage policies."
    )
    categories: ModerationCategories = Field(
        ...,
        description="A dictionary of per-category binary content policy violation flags.",
    )
    category_scores: ModerationCategoryScores = Field(
        ..., description="A dictionary of per-category raw scores output by the model."
    )


class Moderation(BaseModel):
    id: str = Field(
        ..., description="The unique identifier for the moderation request."
    )
    model: str = Field(
        ..., description="The model used to generate the moderation results."
    )
    results: List[ModerationResult] = Field(
        ..., description="A list of moderation objects."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "modr-XXXXX",
                "model": "text-moderation-007",
                "results": [
                    {
                        "flagged": True,
                        "categories": {
                            "sexual": False,
                            "hate": False,
                            "harassment": False,
                            "self-harm": False,
                            "sexual/minors": False,
                            "hate/threatening": False,
                            "violence/graphic": False,
                            "self-harm/intent": False,
                            "self-harm/instructions": False,
                            "harassment/threatening": True,
                            "violence": True,
                        },
                        "category_scores": {
                            "sexual": 1.2282071e-06,
                            "hate": 0.010696256,
                            "harassment": 0.29842457,
                            "self-harm": 1.5236925e-08,
                            "sexual/minors": 5.7246268e-08,
                            "hate/threatening": 0.0060676364,
                            "violence/graphic": 4.435014e-06,
                            "self-harm/intent": 8.098441e-10,
                            "self-harm/instructions": 2.8498655e-11,
                            "harassment/threatening": 0.63055265,
                            "violence": 0.99011886,
                        },
                    }
                ],
            }
        }
    )


class CreateModerationRequest(BaseModel):
    input: Union[str, List[str]] = Field(..., description="The input text to classify")
    model: ModerationModel = Field(
        default=ModerationModel.LATEST, description="The model to use for moderation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input": "I want to kill them.",
                "model": "text-moderation-latest",
            }
        }
    )


# API function signature (this would be implemented elsewhere)


def create_moderation(request: CreateModerationRequest) -> Moderation:
    """Classifies if text is potentially harmful."""
    ...
