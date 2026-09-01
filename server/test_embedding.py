from app.services.embedding_service import generate_embedding


text = """
def login_user(username, password):
    return authenticate(username, password)
"""


embedding = generate_embedding(text)


print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])