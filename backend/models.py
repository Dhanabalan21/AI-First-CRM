from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    hcp_name = Column(
        String(150),
        nullable=False,
        index=True,
    )

    interaction_type = Column(
        String(50),
        nullable=False,
        default="Meeting",
    )

    interaction_date = Column(
        String(20),
        nullable=False,
        default="",
    )

    interaction_time = Column(
        String(20),
        nullable=False,
        default="",
    )

    attendees = Column(
        Text,
        nullable=False,
        default="",
    )

    topics_discussed = Column(
        Text,
        nullable=False,
        default="",
    )

    materials_shared = Column(
        Text,
        nullable=False,
        default="",
    )

    samples_distributed = Column(
        Text,
        nullable=False,
        default="",
    )

    sentiment = Column(
        String(20),
        nullable=False,
        default="Neutral",
    )

    outcomes = Column(
        Text,
        nullable=False,
        default="",
    )

    follow_up_actions = Column(
        Text,
        nullable=False,
        default="",
    )

    summary = Column(
        Text,
        nullable=False,
        default="",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )