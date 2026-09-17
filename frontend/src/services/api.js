// Centralized API layer for the Codebase RAG backend.
// Every network call to FastAPI lives here so components stay UI-only.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    // Network failure: server unreachable, CORS block, DNS, offline, etc.
    throw new ApiError(
      "Can't reach the backend. Make sure the FastAPI server is running.",
      0
    );
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // Non-JSON body; fall through with body = null.
  }

  if (!response.ok) {
    // FastAPI returns { detail: "..." } on HTTPException.
    const detail = body?.detail;
    throw new ApiError(
      typeof detail === "string" ? detail : "The request failed.",
      response.status
    );
  }

  return body;
}

/**
 * Kick off ingestion for a GitHub repository.
 * POST /api/repositories/ingest
 * -> { status, repository_id, github_url, files_found, chunks_created, message }
 */
export function ingestRepository(githubUrl) {
  return request("/api/repositories/ingest", {
    method: "POST",
    body: JSON.stringify({ github_url: githubUrl }),
  });
}

/**
 * Generate embeddings for an already-ingested repository.
 * POST /api/repositories/{repository_id}/embed
 * -> { status, repository_id, chunks_embedded }
 */
export function embedRepository(repositoryId) {
  return request(`/api/repositories/${repositoryId}/embed`, {
    method: "POST",
  });
}

/**
 * Ask a question about an ingested + embedded repository.
 * POST /api/chat
 * -> { status, repository_id, question, answer, sources: [{ file_path, start_line, end_line, score }] }
 */
export function askQuestion(repositoryId, question) {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ repository_id: repositoryId, question }),
  });
}

export { ApiError };
