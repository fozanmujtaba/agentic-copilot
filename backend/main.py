"""FastAPI entrypoint for the Multi-Agent Equity Research Copilot backend."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from llm import active_config  # noqa: E402  (must follow load_dotenv)

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


def _key_is_real(name: str) -> bool:
    """A key copied straight from .env.example is not a usable key."""
    value = os.getenv(name, "").strip()
    return bool(value) and not value.startswith("your-")


@app.get("/health")
async def health():
    """Reports whether the active LLM provider and tracing are usable."""
    llm = active_config()
    return {
        "status": "healthy",
        "llm_provider": llm["provider"],
        "llm_model": llm["model"],
        "llm_key_configured": llm["key_configured"],
        "langsmith_key_loaded": _key_is_real("LANGSMITH_API_KEY"),
    }
