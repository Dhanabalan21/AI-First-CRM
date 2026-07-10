from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


SentimentType = Literal[
    "Positive",
    "Neutral",
    "Negative",
]


class InteractionBase(BaseModel):
    hcp_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    interaction_type: str = "Meeting"

    interaction_date: str = ""

    interaction_time: str = ""

    attendees: str = ""

    topics_discussed: str = ""

    materials_shared: str = ""

    samples_distributed: str = ""

    sentiment: SentimentType = "Neutral"

    outcomes: str = ""

    follow_up_actions: str = ""

    summary: str = ""

    @field_validator(
        "hcp_name",
        "interaction_type",
        "interaction_date",
        "interaction_time",
        "attendees",
        "topics_discussed",
        "materials_shared",
        "samples_distributed",
        "outcomes",
        "follow_up_actions",
        "summary",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None

    interaction_type: Optional[str] = None

    interaction_date: Optional[str] = None

    interaction_time: Optional[str] = None

    attendees: Optional[str] = None

    topics_discussed: Optional[str] = None

    materials_shared: Optional[str] = None

    samples_distributed: Optional[str] = None

    sentiment: Optional[SentimentType] = None

    outcomes: Optional[str] = None

    follow_up_actions: Optional[str] = None

    summary: Optional[str] = None

    @field_validator(
        "hcp_name",
        "interaction_type",
        "interaction_date",
        "interaction_time",
        "attendees",
        "topics_discussed",
        "materials_shared",
        "samples_distributed",
        "outcomes",
        "follow_up_actions",
        "summary",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class InteractionResponse(InteractionBase):
    id: int

    created_at: str | None = None

    updated_at: str | None = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=3,
        max_length=3000,
    )