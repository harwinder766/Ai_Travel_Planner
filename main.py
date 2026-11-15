import logging
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from agent.agentic_workflow import get_graph
from config import settings

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Travel Planner API",
    version="0.1.0",
    description="A reliable API for generating AI-assisted travel plans.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=4000,
        description="A travel planning request.",
    )


class QueryResponse(BaseModel):
    answer: str


def _message_content(message: Any) -> str:
    if isinstance(message, AIMessage):
        content = message.content
    else:
        content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    return str(content)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query_travel_agent(query: QueryRequest) -> QueryResponse:
    try:
        graph = get_graph(settings.model_provider)
        output = graph.invoke({"messages": [("user", query.question)]})
        messages = output.get("messages", [])
        if not messages:
            raise RuntimeError("The travel agent returned no messages.")
        return QueryResponse(answer=_message_content(messages[-1]))
    except (RuntimeError, ValueError) as exc:
        logger.warning("Travel query could not be completed: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected travel query failure")
        raise HTTPException(
            status_code=500,
            detail="The travel agent could not complete the request.",
        ) from exc
