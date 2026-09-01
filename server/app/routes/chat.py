from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest
from app.services.chat_service import generate_answer


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post("")
def chat(request: ChatRequest):

    try:

        answer = generate_answer(
            repository_id=request.repository_id,
            question=request.question
        )

        return {
            "status": "success",
            "repository_id": request.repository_id,
            "question": request.question,
            "answer": answer["answer"],
            "sources": answer["sources"]
}

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )