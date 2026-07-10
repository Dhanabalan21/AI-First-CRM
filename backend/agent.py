import json
import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from models import Interaction

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "gemma2-9b-it",
)

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to the backend/.env file."
    )

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0,
)


class AgentState(TypedDict):
    message: str
    intent: str


def classify_intent(
    state: AgentState,
) -> dict:
    message = state["message"].lower().strip()

    if any(
        phrase in message
        for phrase in (
            "edit interaction",
            "change interaction",
            "update interaction",
            "modify interaction",
        )
    ):
        intent = "edit_interaction"

    elif any(
        phrase in message
        for phrase in (
            "list all interactions",
            "show all interactions",
            "list interactions",
            "recent interactions",
        )
    ):
        intent = "list_interactions"

    elif any(
        phrase in message
        for phrase in (
            "show interaction",
            "get interaction",
            "view interaction",
        )
    ):
        intent = "get_interaction"

    elif (
        message.startswith("suggest follow-up")
        or message.startswith(
            "recommend follow-up"
        )
        or "what should i do next" in message
    ):
        intent = "suggest_follow_up"

    else:
        intent = "log_interaction"

    return {
        "intent": intent,
    }


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node(
        "classify_intent",
        classify_intent,
    )

    workflow.set_entry_point(
        "classify_intent"
    )

    workflow.add_edge(
        "classify_intent",
        END,
    )

    return workflow.compile()


agent_graph = build_graph()


def clean_json_response(
    content: str,
) -> dict:
    cleaned = content.strip()

    cleaned = cleaned.replace(
        "```json",
        "",
    )

    cleaned = cleaned.replace(
        "```",
        "",
    )

    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "The LLM did not return valid JSON."
        )

    json_text = cleaned[start : end + 1]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Unable to parse the LLM JSON response."
        ) from exc


def interaction_to_dict(
    item: Interaction,
) -> dict:
    return {
        "id": item.id,
        "hcp_name": item.hcp_name,
        "interaction_type": (
            item.interaction_type
        ),
        "interaction_date": (
            item.interaction_date
        ),
        "interaction_time": (
            item.interaction_time
        ),
        "attendees": item.attendees,
        "topics_discussed": (
            item.topics_discussed
        ),
        "materials_shared": (
            item.materials_shared
        ),
        "samples_distributed": (
            item.samples_distributed
        ),
        "sentiment": item.sentiment,
        "outcomes": item.outcomes,
        "follow_up_actions": (
            item.follow_up_actions
        ),
        "summary": item.summary,
        "created_at": (
            item.created_at.isoformat()
            if item.created_at
            else None
        ),
        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        ),
    }


def log_interaction_tool(
    message: str,
) -> dict:
    prompt = f"""
You are an AI assistant for a pharmaceutical
Customer Relationship Management system.

Extract structured Healthcare Professional
interaction data from the user's text.

Return valid JSON only.

Use exactly these fields:

hcp_name
interaction_type
interaction_date
interaction_time
attendees
topics_discussed
materials_shared
samples_distributed
sentiment
outcomes
follow_up_actions
summary

Rules:

1. Do not return markdown.
2. Do not add explanations.
3. Do not invent unavailable information.
4. Use an empty string for missing values.
5. Sentiment must be exactly one of:
   Positive, Neutral, Negative.
6. If the message contains "met", "meeting",
   "visited", or "face-to-face", set
   interaction_type to "Meeting".
7. If the message contains "called" or "phone",
   set interaction_type to "Phone Call".
8. If the message contains "email", set
   interaction_type to "Email".
9. Create a short professional summary.
10. Keep dates in YYYY-MM-DD format when possible.
11. Keep times in HH:MM format when possible.

User text:

{message}
"""

    response = llm.invoke(prompt)

    interaction_data = clean_json_response(
        response.content
    )

    return {
        "tool": "log_interaction",
        "message": (
            "Interaction details extracted. "
            "Review the form before saving."
        ),
        "interaction_data": interaction_data,
    }


def list_interactions_tool(
    db: Session,
) -> dict:
    records = (
        db.query(Interaction)
        .order_by(Interaction.id.desc())
        .limit(50)
        .all()
    )

    interactions = [
        interaction_to_dict(item)
        for item in records
    ]

    return {
        "tool": "list_interactions",
        "message": (
            f"Found {len(interactions)} "
            "interaction(s)."
        ),
        "count": len(interactions),
        "interactions": interactions,
    }


def get_interaction_tool(
    message: str,
    db: Session,
) -> dict:
    id_match = re.search(
        r"\d+",
        message,
    )

    if not id_match:
        return {
            "tool": "get_interaction",
            "error": (
                "Please include the "
                "interaction ID."
            ),
        }

    interaction_id = int(
        id_match.group()
    )

    item = (
        db.query(Interaction)
        .filter(
            Interaction.id
            == interaction_id
        )
        .first()
    )

    if not item:
        return {
            "tool": "get_interaction",
            "error": (
                f"Interaction {interaction_id} "
                "was not found."
            ),
        }

    return {
        "tool": "get_interaction",
        "message": (
            f"Interaction {interaction_id} "
            "loaded successfully."
        ),
        "interaction": (
            interaction_to_dict(item)
        ),
    }


def edit_interaction_tool(
    message: str,
    db: Session,
) -> dict:
    id_match = re.search(
        r"\d+",
        message,
    )

    if not id_match:
        return {
            "tool": "edit_interaction",
            "error": (
                "Please include the "
                "interaction ID."
            ),
        }

    interaction_id = int(
        id_match.group()
    )

    item = (
        db.query(Interaction)
        .filter(
            Interaction.id
            == interaction_id
        )
        .first()
    )

    if not item:
        return {
            "tool": "edit_interaction",
            "error": (
                f"Interaction {interaction_id} "
                "was not found."
            ),
        }

    prompt = f"""
You are editing an existing Healthcare
Professional CRM interaction.

Extract only the fields that should be updated
from the user's instruction.

Return valid JSON only.

Allowed fields:

hcp_name
interaction_type
interaction_date
interaction_time
attendees
topics_discussed
materials_shared
samples_distributed
sentiment
outcomes
follow_up_actions
summary

Rules:

1. Do not include unchanged fields.
2. Do not include the interaction ID.
3. Do not return markdown.
4. Do not return explanations.
5. Sentiment must be exactly one of:
   Positive, Neutral, Negative.
6. Use an empty JSON object if no valid update
   can be found.

User instruction:

{message}
"""

    response = llm.invoke(prompt)

    updates = clean_json_response(
        response.content
    )

    allowed_fields = {
        "hcp_name",
        "interaction_type",
        "interaction_date",
        "interaction_time",
        "attendees",
        "topics_discussed",
        "materials_shared",
        "samples_distributed",
        "sentiment",
        "outcomes",
        "follow_up_actions",
        "summary",
    }

    updated_fields = {}

    for field, value in updates.items():
        if (
            field in allowed_fields
            and value is not None
            and value != ""
        ):
            setattr(
                item,
                field,
                value,
            )

            updated_fields[field] = value

    if not updated_fields:
        return {
            "tool": "edit_interaction",
            "error": (
                "No valid update information "
                "was found."
            ),
        }

    db.commit()
    db.refresh(item)

    return {
        "tool": "edit_interaction",
        "message": (
            f"Interaction {interaction_id} "
            "updated successfully."
        ),
        "interaction_id": interaction_id,
        "updated_fields": updated_fields,
        "interaction": (
            interaction_to_dict(item)
        ),
    }


def suggest_follow_up_tool(
    message: str,
) -> dict:
    prompt = f"""
You are a pharmaceutical CRM sales assistant.

Based on the user's request, suggest exactly
three concise and professional follow-up actions.

Return only a numbered list.

Do not return markdown headings.

User request:

{message}
"""

    response = llm.invoke(prompt)

    return {
        "tool": "suggest_follow_up",
        "message": (
            "Follow-up suggestions generated."
        ),
        "suggestions": (
            response.content.strip()
        ),
    }


TOOLS = {
    "log_interaction": (
        log_interaction_tool
    ),
    "edit_interaction": (
        edit_interaction_tool
    ),
    "get_interaction": (
        get_interaction_tool
    ),
    "list_interactions": (
        list_interactions_tool
    ),
    "suggest_follow_up": (
        suggest_follow_up_tool
    ),
}


def execute_agent(
    message: str,
    db: Session,
) -> dict:
    state = agent_graph.invoke(
        {
            "message": message,
            "intent": "",
        }
    )

    intent = state["intent"]

    if intent == "log_interaction":
        return TOOLS[intent](message)

    if intent == "edit_interaction":
        return TOOLS[intent](
            message,
            db,
        )

    if intent == "get_interaction":
        return TOOLS[intent](
            message,
            db,
        )

    if intent == "list_interactions":
        return TOOLS[intent](db)

    if intent == "suggest_follow_up":
        return TOOLS[intent](message)

    return {
        "error": (
            "Unable to identify the "
            "requested action."
        )
    }