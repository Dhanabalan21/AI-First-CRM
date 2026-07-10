import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from agent import execute_agent, interaction_to_dict
from database import Base, engine, get_db
from models import Interaction
from schemas import (
    ChatRequest,
    InteractionCreate,
    InteractionUpdate,
)

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Database table creation
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="AI-First HCP CRM",
    version="1.0.0",
    description=(
        "AI-first Healthcare Professional interaction "
        "logging and management API using FastAPI, "
        "LangGraph, Groq, and PostgreSQL."
    ),
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root and health endpoints
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI-First HCP CRM API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health(
    db: Session = Depends(get_db),
):
    database_status = "connected"

    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception(
            "Database health check failed"
        )

        database_status = "disconnected"

        return {
            "status": "unhealthy",
            "database": database_status,
            "llm": "configured",
            "agent_framework": "LangGraph",
            "error": str(exc),
        }

    return {
        "status": "healthy",
        "database": database_status,
        "llm": "configured",
        "agent_framework": "LangGraph",
    }


# ---------------------------------------------------------
# Create interaction
# ---------------------------------------------------------

@app.post(
    "/api/interactions",
    status_code=201,
)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
):
    try:
        item = Interaction(
            **payload.model_dump()
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(
            "Interaction created: id=%s, hcp=%s",
            item.id,
            item.hcp_name,
        )

        return {
            "message": (
                "Interaction saved successfully."
            ),
            "interaction": (
                interaction_to_dict(item)
            ),
        }

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Failed to create interaction"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to save the interaction."
            ),
        ) from exc


# ---------------------------------------------------------
# List, search, and filter interactions
# ---------------------------------------------------------

@app.get("/api/interactions")
def list_interactions(
    search: str = Query(
        default="",
        max_length=100,
    ),
    sentiment: str = Query(
        default="",
        max_length=20,
    ),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Interaction)

        cleaned_search = search.strip()
        cleaned_sentiment = sentiment.strip()

        if cleaned_search:
            search_term = (
                f"%{cleaned_search}%"
            )

            query = query.filter(
                or_(
                    Interaction.hcp_name.ilike(
                        search_term
                    ),
                    Interaction.topics_discussed.ilike(
                        search_term
                    ),
                    Interaction.outcomes.ilike(
                        search_term
                    ),
                    Interaction.summary.ilike(
                        search_term
                    ),
                    Interaction.attendees.ilike(
                        search_term
                    ),
                )
            )

        if cleaned_sentiment:
            allowed_sentiments = {
                "Positive",
                "Neutral",
                "Negative",
            }

            if cleaned_sentiment not in allowed_sentiments:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Sentiment must be "
                        "Positive, Neutral, or Negative."
                    ),
                )

            query = query.filter(
                Interaction.sentiment
                == cleaned_sentiment
            )

        records = (
            query
            .order_by(
                Interaction.id.desc()
            )
            .all()
        )

        return [
            interaction_to_dict(item)
            for item in records
        ]

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to list interactions"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load interactions."
            ),
        ) from exc


# ---------------------------------------------------------
# Get one interaction
# ---------------------------------------------------------

@app.get(
    "/api/interactions/{interaction_id}"
)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    item = (
        db.query(Interaction)
        .filter(
            Interaction.id
            == interaction_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found.",
        )

    return interaction_to_dict(item)


# ---------------------------------------------------------
# Update interaction
# ---------------------------------------------------------

@app.put(
    "/api/interactions/{interaction_id}"
)
def update_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
):
    item = (
        db.query(Interaction)
        .filter(
            Interaction.id
            == interaction_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found.",
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail=(
                "No update fields were provided."
            ),
        )

    try:
        for field, value in update_data.items():
            setattr(
                item,
                field,
                value,
            )

        db.commit()
        db.refresh(item)

        logger.info(
            "Interaction updated: id=%s",
            interaction_id,
        )

        return {
            "message": (
                "Interaction updated successfully."
            ),
            "interaction": (
                interaction_to_dict(item)
            ),
        }

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Failed to update interaction: id=%s",
            interaction_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to update interaction."
            ),
        ) from exc


# ---------------------------------------------------------
# Delete interaction
# ---------------------------------------------------------

@app.delete(
    "/api/interactions/{interaction_id}"
)
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    item = (
        db.query(Interaction)
        .filter(
            Interaction.id
            == interaction_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found.",
        )

    try:
        db.delete(item)
        db.commit()

        logger.info(
            "Interaction deleted: id=%s",
            interaction_id,
        )

        return {
            "message": (
                "Interaction deleted successfully."
            ),
            "interaction_id": interaction_id,
        }

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Failed to delete interaction: id=%s",
            interaction_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to delete interaction."
            ),
        ) from exc


# ---------------------------------------------------------
# LangGraph AI agent endpoint
# ---------------------------------------------------------

@app.post("/api/agent/chat")
def agent_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    message = payload.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    logger.info(
        "AI request received: %s",
        message[:120],
    )

    try:
        result = execute_agent(
            message,
            db,
        )

        logger.info(
            "AI tool used: %s",
            result.get(
                "tool",
                "unknown",
            ),
        )

        return result

    except ValueError as exc:
        logger.warning(
            "AI validation error: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "AI agent request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI assistant could not "
                "process the request."
            ),
        ) from exc