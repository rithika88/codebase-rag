from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.mongodb import client
from app.routes.repository import router as repository_router
from app.routes.search import router as search_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="Codebase RAG Assistant",
    description="AI assistant for understanding codebases",
    version="1.0.0"
)

# Allow the Vite dev server (and any local dev port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(repository_router)
app.include_router(search_router)
app.include_router(chat_router)

@app.get("/api/health")
def health_check():

    try:
        client.admin.command("ping")

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }