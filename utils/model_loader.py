import os
from dotenv import load_dotenv
from pydantic import BaseModel,Field
from typing import Optional, Literal, Any
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_gemini import ChatGemini
from config import settings

class ModelLoader:
    def __init__(self, model_name: Literal["groq", "openai", "gemini"] = "groq"):
        self.model_name = model_name
        self.model = self.load_model()
        
    def load_model(self) -> Any:
        if self.model_name == "groq":
            return ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
        elif self.model_name == "openai":
            return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.model_name == "gemini":
            return ChatGemini(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
        else:
            raise ValueError(f"Unsupported model name: {self.model_name}")