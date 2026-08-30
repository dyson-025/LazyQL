from fastapi import APIRouter, HTTPException, Depends

from app.ai.gemini import GeminiService
from app.ai.service import AIService

from app.database.session_manager import session_manager
from app.models.generate import (
    GenerateRequest,
    GenerateResponse,
)

router = APIRouter(prefix="/generate", tags=["AI"])

_default_ai_service = GeminiService()


def get_ai_service() -> AIService:
    return _default_ai_service


@router.post("", response_model=GenerateResponse)
def generate_sql(
    request: GenerateRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    try:
        db = session_manager.get_session(
            request.session_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Database session not found",
        ) from exc

    schema = db.get_schema()

    result = ai_service.generate_sql(
        request.question,
        schema.model_dump(),
    )

    return GenerateResponse(**result)