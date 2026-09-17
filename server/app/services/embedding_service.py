from sentence_transformers import SentenceTransformer
from pymongo import UpdateOne

from app.database.mongodb import code_chunks_collection


# Load the lightweight 80MB embedding model once on Apple Silicon GPU
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding for a single piece of text
    using the lightweight local model on Apple Silicon GPU.
    """
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def embed_repository_chunks(repository_id: str) -> int:
    """
    Generate embeddings for all chunks belonging to a repository
    using local Apple Silicon GPU in ~1 second, and update MongoDB via bulk_write.
    """
    chunks = list(
        code_chunks_collection.find(
            {"repository_id": repository_id},
            {"_id": 1, "content": 1}
        )
    )

    if not chunks:
        return 0

    texts = [chunk["content"] for chunk in chunks]

    # Fast local encoding on GPU (0.8s for 100+ chunks)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    operations = [
        UpdateOne(
            {"_id": chunk["_id"]},
            {"$set": {"embedding": embedding.tolist()}}
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    if operations:
        code_chunks_collection.bulk_write(operations, ordered=False)

    return len(operations)