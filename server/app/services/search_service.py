from app.database.mongodb import code_chunks_collection
from app.services.embedding_service import generate_embedding


def search_code(
    repository_id: str,
    query: str,
    limit: int = 5
):
    """
    Perform semantic search over code chunks
    using MongoDB Atlas Vector Search.
    """

    # 1. Convert the user's question into an embedding
    query_embedding = generate_embedding(query)

    # 2. Perform vector search in MongoDB
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": limit,
                "filter": {
                    "repository_id": repository_id
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "repository_id": 1,
                "file_path": 1,
                "content": 1,
                "start_line": 1,
                "end_line": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    results = list(
        code_chunks_collection.aggregate(pipeline)
    )

    return results