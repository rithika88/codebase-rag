import os

from google import genai

from app.services.search_service import search_code


def generate_answer(
    repository_id: str,
    question: str
):

    # 1. Retrieve relevant chunks
    results = search_code(
        repository_id=repository_id,
        query=question,
        limit=5
    )

    if not results:
        return {
            "answer": "I couldn't find relevant information in this repository.",
            "sources": []
        }

    # 2. Build context
    context_parts = []
    sources = []

    for result in results:

        context_parts.append(
            f"""
File: {result["file_path"]}
Lines: {result["start_line"]}-{result["end_line"]}

{result["content"]}
"""
        )

        sources.append({
            "file_path": result["file_path"],
            "start_line": result["start_line"],
            "end_line": result["end_line"],
            "score": result["score"]
        })

    context = "\n\n".join(context_parts)

    # 3. Create RAG prompt
    prompt = f"""
You are a codebase assistant.

Answer the user's question using ONLY the repository
context provided below.

If the answer cannot be found in the context,
say that you could not find the answer in the repository.

Be clear and concise.

User question:
{question}

Repository context:
{context}
"""

    # 4. Get Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception("GEMINI_API_KEY is not configured")

    # 5. Create Gemini client
    client = genai.Client(
        api_key=api_key
    )

    # 6. Generate answer
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    answer = interaction.output_text

    # 7. Return answer + sources
    return {
        "answer": answer,
        "sources": sources
    }