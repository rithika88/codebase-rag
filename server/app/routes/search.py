from fastapi import APIRouter, HTTPException

from app.models.search import SearchRequest
from app.services.search_service import search_code


router = APIRouter(
    prefix="/api/search",
    tags=["Search"]
)


@router.post("")
def search_repository(request: SearchRequest):

    try:

        results = search_code(
            repository_id=request.repository_id,
            query=request.query,
            limit=request.limit
        )

        return {
            "status": "success",
            "repository_id": request.repository_id,
            "query": request.query,
            "results": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )