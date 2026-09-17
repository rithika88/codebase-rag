from app.database.mongodb import code_chunks_collection
from app.services.embedding_service import generate_embedding


# Files that are especially useful for documentation,
# setup, dependencies, and project overview questions.
DOCUMENTATION_FILES = {
    "README",
    "README.md",
    "README.txt",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    ".env.example",
}


def search_code(
    repository_id: str,
    query: str,
    limit: int = 10
):
    """
    Perform semantic search over repository chunks
    using MongoDB Atlas Vector Search.

    The search retrieves more candidates than the final
    requested limit so the chat service has better context.
    """

    query = query.strip()

    if not query:
        return []

    # ---------------------------------------------------------
    # 1. Convert question into an embedding
    # ---------------------------------------------------------

    query_embedding = generate_embedding(query)

    # ---------------------------------------------------------
    # 2. Retrieve more candidates from Vector Search
    # ---------------------------------------------------------

    candidate_limit = max(limit * 3, 30)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": candidate_limit,
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

    if not results:
        return []

    # ---------------------------------------------------------
    # 3. Detect question intent
    # ---------------------------------------------------------

    query_lower = query.lower()

    documentation_keywords = [
        "clone",
        "install",
        "installation",
        "setup",
        "set up",
        "run",
        "running",
        "start",
        "prerequisite",
        "prerequisites",
        "dependency",
        "dependencies",
        "technology",
        "technologies",
        "tech stack",
        "framework",
        "library",
        "libraries",
        "environment variable",
        "configuration",
        "usage",
        "how to use",
        "overview",
    ]

    implementation_keywords = [
        "where is",
        "where are",
        "implemented",
        "implementation",
        "logic",
        "which file",
        "what file",
        "handles",
        "handled by",
        "function",
        "class",
        "method",
        "code",
    ]

    documentation_question = any(
        keyword in query_lower
        for keyword in documentation_keywords
    )

    implementation_question = any(
        keyword in query_lower
        for keyword in implementation_keywords
    )

    # ---------------------------------------------------------
    # 4. Give documentation files a boost when appropriate
    # ---------------------------------------------------------

    if documentation_question:

        for result in results:

            filename = result["file_path"].split("/")[-1]

            if filename in DOCUMENTATION_FILES:

                # Small ranking boost.
                result["score"] = result["score"] + 0.15

    # ---------------------------------------------------------
    # 5. Prefer source files for implementation questions
    # ---------------------------------------------------------

    if implementation_question:

        source_extensions = (
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".kts",
        )

        for result in results:

            filename = result["file_path"].split("/")[-1]
            file_path = result["file_path"].lower()

            # Strongly prefer actual source-code files
            if file_path.endswith(source_extensions):
                result["score"] = result["score"] + 0.20

            # De-prioritize styling files
            if file_path.endswith(
                (".css", ".scss", ".less")
            ):
                result["score"] = result["score"] - 0.15

            # De-prioritize build/tooling configuration
            if filename in {
                "eslint.config.js",
                "vite.config.js",
                "webpack.config.js",
            }:
                result["score"] = result["score"] - 0.10

    # ---------------------------------------------------------
    # 6. Sort by final score
    # ---------------------------------------------------------

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    # ---------------------------------------------------------
    # 7. Remove duplicate file/line combinations
    # ---------------------------------------------------------

    unique_results = []
    seen = set()

    for result in results:

        key = (
            result["file_path"],
            result["start_line"],
            result["end_line"]
        )

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    # ---------------------------------------------------------
    # 8. Return best results
    # ---------------------------------------------------------

    return unique_results[:limit]