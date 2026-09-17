import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.database.mongodb import repositories_collection
from app.services.search_service import search_code

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)
CHAT_MODEL = "gemini-2.5-flash"


def generate_answer(
    repository_id: str,
    question: str
):
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question about the repository.",
            "sources": []
        }

    # ---------------------------------------------------------
    # 1. Handle simple conversation
    # ---------------------------------------------------------

    simple_questions = {
        "hi",
        "hello",
        "hey",
        "hi there",
        "hello there",
    }

    if question.lower() in simple_questions:
        return {
            "answer": (
                "Hi! I can help you understand this repository. "
                "You can ask me about its architecture, code, "
                "dependencies, APIs, setup, technologies, or "
                "how different parts of the project work."
            ),
            "sources": []
        }

    # ---------------------------------------------------------
    # 2. Get repository metadata
    # ---------------------------------------------------------

    repository = repositories_collection.find_one(
        {
            "repository_id": repository_id
        },
        {
            "_id": 0
        }
    )

    if not repository:
        return {
            "answer": (
                "I couldn't find this repository in the database."
            ),
            "sources": []
        }

    github_url = repository.get(
        "github_url",
        "Not available"
    )

    files_found = repository.get(
        "files_found",
        "Unknown"
    )

    chunks_created = repository.get(
        "chunks_created",
        "Unknown"
    )

    # ---------------------------------------------------------
    # 3. Search repository
    # ---------------------------------------------------------

    results = search_code(
        repository_id=repository_id,
        query=question,
        limit=10
    )

    # ---------------------------------------------------------
    # 4. Build repository context
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 5. Build repository metadata context
    # ---------------------------------------------------------

    metadata_context = f"""
Repository URL: {github_url}
Files indexed: {files_found}
Chunks indexed: {chunks_created}
"""

    # ---------------------------------------------------------
    # 6. Prompt
    # ---------------------------------------------------------

    prompt = f"""
You are an expert AI assistant for a GitHub repository.

Your job is to help the user understand the repository accurately.

You have two types of repository information:
1. Repository metadata
2. Retrieved source-code/documentation chunks

Use both when answering.

IMPORTANT RULES:
1. The repository itself is the source of truth.
2. Never invent files, functions, dependencies, technologies, commands, APIs, or implementation details.
3. Use the actual repository URL from the metadata when answering questions about cloning or the repository URL.
4. If the user asks "How do I clone this repository?", provide the actual GitHub URL from the metadata.
5. If the user asks about dependencies, inspect dependency files such as package.json, requirements.txt, pom.xml, pyproject.toml, etc. when they are present in the context.
6. If the user asks how to run the project, use README, package files, configuration files, Docker files and source code available in the context.
7. If the user asks where something is implemented, identify the actual file and explain the relevant logic from the retrieved source code.
8. If the user asks about architecture, synthesize the architecture from multiple relevant files rather than relying only on README.
9. README.md is optional. Do not assume that a repository must contain a README.
10. If there is no README, use source files and configuration files to understand the project.
11. If the retrieved context contains enough information, answer the question.
12. If only part of the answer is available, give the available information and clearly state what could not be determined.
13. Answer naturally, like a helpful senior developer explaining the project to another developer. Use clear formatting with Markdown code blocks where helpful.

REPOSITORY METADATA:
{metadata_context}

RETRIEVED REPOSITORY CONTEXT:
{context if context else "No directly matching code chunks were retrieved."}

USER QUESTION:
{question}
"""

    # ---------------------------------------------------------
    # 7. Generate answer using Google Gemini
    # ---------------------------------------------------------

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )

    answer = response.text.strip() if response.text else "No response generated."

    # ---------------------------------------------------------
    # 8. Return response
    # ---------------------------------------------------------

    return {
        "answer": answer,
        "sources": sources
    }