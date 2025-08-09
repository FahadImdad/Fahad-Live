from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.services import knowledge_svc

router = APIRouter()


class RespondRequest(BaseModel):
    transcript: str
    visionContext: Optional[str] = None
    class Meta(BaseModel):
        lang: Optional[str] = None
    meta: Optional[Meta] = None


class Sentiment(BaseModel):
    valence: float = 0.0
    arousal: float = 0.0


class RespondResponse(BaseModel):
    text: str
    sentiment: Sentiment
    snippets: List[str] = []


def _needs_personal_info(text: str) -> bool:
    keywords = {
        "who", "bio", "project", "cv", "resume", "publication",
        "portfolio", "experience", "talk", "contact", "work"
    }
    lowered = text.lower()
    return any(word in lowered for word in keywords)


@router.post("/respond", response_model=RespondResponse)
async def respond(payload: RespondRequest) -> RespondResponse:
    snippets: List[str] = []
    if _needs_personal_info(payload.transcript):
        snippets = await knowledge_svc.fetch_personal_snippets(payload.transcript)
    # Placeholder response – integration with LLM to be added
    text = "Acknowledged: " + payload.transcript
    return RespondResponse(text=text, sentiment=Sentiment(), snippets=snippets)
