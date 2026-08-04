# Multi-Agent Equity Research Copilot

A multi-agent system for equity research, built with LangGraph and Next.js.

> **Status:** Phase 1 — project scaffolding. Agents are not implemented yet.

## Stack

| Layer     | Technology                                                     |
| --------- | -------------------------------------------------------------- |
| Backend   | Python 3.11, FastAPI, LangGraph, ChromaDB, pandas               |
| Models    | Google Gemini (`langchain-google-genai`)                        |
| Tracing   | LangSmith                                                       |
| Frontend  | Next.js (App Router), TypeScript, Tailwind CSS, Vercel AI SDK   |

## Layout

```
agentic-copilot/
├── backend/     # FastAPI server + LangGraph agents
└── frontend/    # Next.js application
```

## Getting started

### Backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API keys
uvicorn main:app --reload --port 8000
```

Verify at http://localhost:8000/ — `/health` reports whether your API keys loaded.
Interactive docs at http://localhost:8000/docs.

### Frontend

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
cd frontend
npm install ai @ai-sdk/react
npm run dev
```

Runs at http://localhost:3000, which is the origin allowed by the backend's CORS config.

## Configuration

Copy `backend/.env.example` to `backend/.env` and fill in:

- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/apikey)
- `LANGSMITH_API_KEY` — from [LangSmith](https://smith.langchain.com/)

`.env` is gitignored. Never commit real keys.
