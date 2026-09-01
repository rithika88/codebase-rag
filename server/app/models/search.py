from pydantic import BaseModel, Field


class SearchRequest(BaseModel):

    repository_id: str

    query: str

    limit: int = Field(
        default=5,
        ge=1,
        le=20
    )