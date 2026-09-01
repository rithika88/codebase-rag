import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.repository import RepositoryRequest
from app.services.github_service import clone_repository
from app.services.parser_service import (
    get_source_files,
    chunk_code
)
from app.database.mongodb import (
    repositories_collection,
    code_chunks_collection
)
from app.services.embedding_service import embed_repository_chunks


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"]
)


@router.post("/ingest")
def ingest_repository(request: RepositoryRequest):

    repository_id = str(uuid.uuid4())

    try:

        # --------------------------------
        # 1. Clone repository
        # --------------------------------

        repo_path = clone_repository(
            str(request.github_url),
            repository_id
        )

        # --------------------------------
        # 2. Find source files
        # --------------------------------

        source_files = get_source_files(
            repo_path
        )

        # --------------------------------
        # 3. Create code chunks
        # --------------------------------

        all_chunks = []

        for file_path in source_files:

            chunks = chunk_code(
                file_path,
                repo_path
            )

            all_chunks.extend(chunks)

        # --------------------------------
        # 4. Save repository information
        # --------------------------------

        repository_document = {
            "repository_id": repository_id,
            "github_url": str(request.github_url),
            "files_found": len(source_files),
            "chunks_created": len(all_chunks),
            "created_at": datetime.now(timezone.utc)
        }

        repositories_collection.insert_one(
            repository_document
        )

        # --------------------------------
        # 5. Save code chunks
        # --------------------------------

        chunk_documents = []

        for chunk in all_chunks:

            chunk_documents.append({
                "repository_id": repository_id,
                "file_path": chunk["file_path"],
                "content": chunk["content"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"]
            })

        if chunk_documents:

            code_chunks_collection.insert_many(
                chunk_documents
            )

        # --------------------------------
        # 6. Response
        # --------------------------------

        return {
            "status": "success",
            "repository_id": repository_id,
            "github_url": str(request.github_url),
            "files_found": len(source_files),
            "chunks_created": len(all_chunks),
            "message": "Repository successfully ingested"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{repository_id}/embed")
def embed_repository(repository_id: str):

    try:

        count = embed_repository_chunks(
            repository_id
        )

        return {
            "status": "success",
            "repository_id": repository_id,
            "chunks_embedded": count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )