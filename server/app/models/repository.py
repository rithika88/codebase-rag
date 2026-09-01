from pydantic import BaseModel, HttpUrl


class RepositoryRequest(BaseModel):
    github_url: HttpUrl