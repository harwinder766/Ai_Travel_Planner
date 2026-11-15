from typing import Any, Literal

from config import settings

ModelName = Literal["groq", "openai", "gemini"]


class ModelLoader:
    def __init__(self, model_name: ModelName = "groq"):
        self.model_name = model_name

    def load_model(self) -> Any:
        api_key = settings.require_model_api_key()

        if self.model_name == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                api_key=api_key,
                model=settings.groq_model,
            )

        if self.model_name == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                api_key=api_key,
                model=settings.openai_model,
            )

        if self.model_name == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError as exc:
                raise RuntimeError(
                    "Gemini support requires the 'langchain-google-genai' package."
                ) from exc

            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=settings.gemini_model,
            )

        raise ValueError(f"Unsupported model name: {self.model_name}")

    def __call__(self) -> Any:
        return self.load_model()
