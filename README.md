# AI-First HCP CRM

An AI-powered Healthcare Professional (HCP) Customer Relationship Management system.

---

## Tech Stack

### Frontend

- React
- Redux Toolkit
- Axios
- Google Inter Font

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- LangGraph
- Groq LLM (gemma2-9b-it)

---

## AI Agent Tools

The LangGraph AI Agent supports five tools:

1. Log Interaction
2. Edit Interaction
3. Get Interaction
4. List Interactions
5. Suggest Follow-Up

---

## Installation

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Backend URL

```
http://127.0.0.1:8000
```

---

## Frontend URL

```
http://localhost:5173
```

---

## Demo Prompts

### Log Interaction

```
Met Dr. Smith today.
Discussed Product X.
Doctor requested a brochure.
Follow-up next week.
```

---

### List Interactions

```
List all interactions
```

---

### Show Interaction

```
Show interaction 1
```

---

### Edit Interaction

```
Edit interaction 1 and change the sentiment to Positive
```

---

### Suggest Follow-Up

```
Suggest follow-up for Dr. Smith
```

---

## Developed By

Dhanabalan