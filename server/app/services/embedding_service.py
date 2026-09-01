from sentence_transformers import SentenceTransformer

from app.database.mongodb import code_chunks_collection


# Load the embedding model once when the application starts
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embedding(text: str):
    """
    Generate an embedding for a single piece of text.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def embed_repository_chunks(repository_id: str):
    """
    Generate embeddings for all chunks belonging
    to a repository.
    """

    chunks = list(
        code_chunks_collection.find(
            {
                "repository_id": repository_id
            }
        )
    )

    if not chunks:
        return 0

    # Get all chunk contents
    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    # Generate all embeddings locally
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    updated_count = 0

    # Store each embedding in MongoDB
    for chunk, embedding in zip(chunks, embeddings):

        code_chunks_collection.update_one(
            {
                "_id": chunk["_id"]
            },
            {
                "$set": {
                    "embedding": embedding.tolist()
                }
            }
        )

        updated_count += 1

    return updated_count