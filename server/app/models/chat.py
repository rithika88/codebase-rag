from pydantic import BaseModel


class ChatRequest(BaseModel):
    repository_id: str
    question: str