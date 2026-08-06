"""Provider-agnostic LLM factory.

Agent code calls `get_llm()` and never names a provider, so switching models
is an .env change rather than a refactor.

Client libraries are imported inside each branch on purpose: only the selected
provider's dependencies are ever loaded, so an unused provider costs disk space
but no resident memory.
"""

import os

DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.5-flash",
    "cerebras": "llama-3.3-70b",
    "ollama": "llama3.1:8b",
}

# Free tiers rate-limit aggressively (Groq is ~30 req/min), and a fan-out of
# parallel agents will hit that ceiling. Retry with backoff rather than failing
# the whole graph on one 429.
MAX_ATTEMPTS = 5


class MissingAPIKeyError(RuntimeError):
    """Raised with a fix, not just a complaint."""

    def __init__(self, provider: str, env_var: str, url: str):
        super().__init__(
            f"{provider} selected but {env_var} is not set. "
            f"Get a key at {url} and add it to backend/.env"
        )


def _require(env_var: str, provider: str, url: str) -> str:
    value = os.getenv(env_var, "").strip()
    if not value or value.startswith("your-"):
        raise MissingAPIKeyError(provider, env_var, url)
    return value


def _missing_package(provider: str, package: str) -> RuntimeError:
    """Only groq and gemini ship installed; the rest are opt-in extras."""
    return RuntimeError(
        f"LLM_PROVIDER={provider} requires the {package} package. "
        f"Install it with: pip install {package}"
    )


def get_llm(provider: str | None = None, model: str | None = None, temperature: float = 0.0, **kwargs):
    """Return a chat model for the configured provider.

    Args:
        provider: Overrides LLM_PROVIDER. One of DEFAULT_MODELS.
        model: Overrides LLM_MODEL, then the provider's default.
        temperature: Defaults to 0.0 — research output should be reproducible.
    """
    provider = (provider or os.getenv("LLM_PROVIDER", "groq")).strip().lower()
    model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(provider)

    if provider == "groq":
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=_require("GROQ_API_KEY", "groq", "https://console.groq.com/keys"),
            **kwargs,
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=_require(
                "GEMINI_API_KEY", "gemini", "https://aistudio.google.com/apikey"
            ),
            **kwargs,
        )

    elif provider == "cerebras":
        try:
            from langchain_cerebras import ChatCerebras
        except ImportError as e:
            raise _missing_package(provider, "langchain-cerebras") from e

        llm = ChatCerebras(
            model=model,
            temperature=temperature,
            api_key=_require(
                "CEREBRAS_API_KEY", "cerebras", "https://cloud.cerebras.ai"
            ),
            **kwargs,
        )

    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise _missing_package(provider, "langchain-ollama") from e

        # Local inference — no API key, but the model must be pulled first.
        llm = ChatOllama(model=model, temperature=temperature, **kwargs)

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER {provider!r}. Expected one of: {', '.join(DEFAULT_MODELS)}"
        )

    return llm.with_retry(
        wait_exponential_jitter=True,
        stop_after_attempt=MAX_ATTEMPTS,
    )


def active_config() -> dict:
    """Describe the current selection without constructing a client."""
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    key_var = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
        "ollama": None,
    }.get(provider)

    key_value = os.getenv(key_var, "").strip() if key_var else ""
    return {
        "provider": provider,
        "model": os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(provider),
        "key_configured": True if key_var is None else bool(key_value)
        and not key_value.startswith("your-"),
    }
