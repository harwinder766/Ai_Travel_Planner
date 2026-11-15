import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if not value:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    model_provider: str = os.getenv("MODEL_PROVIDER", "groq").lower()
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    openweathermap_api_key: str | None = os.getenv("OPENWEATHERMAP_API_KEY")
    exchange_rate_api_key: str | None = os.getenv("EXCHANGE_RATE_API_KEY")
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    gplaces_api_key: str | None = os.getenv("GPLACES_API_KEY")
    cors_origins: tuple[str, ...] = _csv(
        os.getenv("CORS_ORIGINS"),
        ("http://localhost:8501",),
    )

    def require_model_api_key(self) -> str:
        if self.model_provider not in {"groq", "openai", "gemini"}:
            raise ValueError(
                f"Unsupported model provider '{self.model_provider}'. "
                "Choose groq, openai, or gemini."
            )
        key = {
            "groq": self.groq_api_key,
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
        }.get(self.model_provider)
        if not key:
            environment_variable = {
                "groq": "GROQ_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": "GEMINI_API_KEY",
            }[self.model_provider]
            raise RuntimeError(
                f"Missing API key for model provider '{self.model_provider}'. "
                f"Set {environment_variable}."
            )
        return key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
