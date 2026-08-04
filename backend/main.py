"""FastAPI entrypoint for the Multi-Agent Equity Research Copilot backend."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="Equity Research Copilot API",
    description="Backend for the multi-agent equity research copilot.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "equity-research-copilot", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Reports whether the API keys the agents will need are actually loaded."""
    return {
        "status": "healthy",
        "gemini_key_loaded": bool(os.getenv("GEMINI_API_KEY")),
        "langsmith_key_loaded": bool(os.getenv("LANGSMITH_API_KEY")),
    }
