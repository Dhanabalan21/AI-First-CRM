# AI-First CRM – HCP Log Interaction Module

An AI-powered Customer Relationship Management (CRM) application designed for Healthcare Professionals (HCPs). The system enables medical representatives to log HCP interactions using either a structured form or a conversational AI assistant. It leverages LangGraph and Groq LLM to extract structured information, summarize conversations, and recommend follow-up actions.

---

## Features

- Log HCP interactions through a structured form
- Log interactions using natural language via AI chat
- AI-powered extraction of interaction details
- Edit existing interactions
- Retrieve individual interactions
- List all logged interactions
- AI-generated follow-up suggestions
- RESTful APIs using FastAPI
- SQL database integration
- Responsive React frontend with Redux state management

---

## Tech Stack

### Frontend

- React
- Redux Toolkit
- Axios
- Vite
- Google Inter Font

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite
- LangGraph
- Groq LLM
- Pydantic

---

## AI Agent Tools

The LangGraph AI Agent provides the following tools:

1. **Log Interaction**
2. **Edit Interaction**
3. **Get Interaction**
4. **List Interactions**
5. **Suggest Follow-Up**

---

## Project Structure

```text
AI-First-CRM/
│
├── backend/
│   ├── agent.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Dhanabalan21/AI-First-CRM.git

cd AI-First-CRM
```

---

### 2. Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file using `.env.example` and add your Groq API key.

Example:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=sqlite:///./hcp_crm.db
```

Run the backend:

```bash
uvicorn main:app --reload
```

Backend API:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

### 3. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:5173
```

---

## AI Workflow

```text
User
   │
   ▼
React Frontend
   │
   ▼
FastAPI Backend
   │
   ▼
LangGraph AI Agent
   │
   ▼
Groq LLM
   │
   ▼
SQL Database
```

---

## Example AI Prompts

### Log Interaction

```text
Met Dr. Smith today.
Discussed Product X efficacy.
Doctor showed positive interest.
Shared the product brochure.
Follow up next week.
```

---

### List Interactions

```text
List all interactions
```

---

### Get Interaction

```text
Show interaction 1
```

---

### Edit Interaction

```text
Edit interaction 1 and change the sentiment to Positive
```

---

### Suggest Follow-Up

```text
Suggest follow-up for Dr. Smith
```

---

## API Documentation

After starting the backend, open:

```
http://127.0.0.1:8000/docs
```

to test all available REST APIs.

---

## Author

**Dhanabalan**

GitHub: https://github.com/Dhanabalan21

---
