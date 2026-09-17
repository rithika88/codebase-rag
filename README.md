# 🔍 Codebase RAG Assistant

An AI-powered assistant that lets you **chat with any GitHub repository**. Point it at a public repo, and ask anything — architecture questions, how to run it, where a feature is implemented, what dependencies it uses — and get accurate, grounded answers with cited source files and line numbers.

---

## ✨ Features

- **Universal Codebase Understanding** — works with any public GitHub repository across 15+ languages (Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, and more).
- **Semantic Vector Search** — embeds code chunks using `all-MiniLM-L6-v2` and stores them in MongoDB Atlas Vector Search for fast, relevant retrieval.
- **Intent-Aware Re-ranking** — automatically boosts documentation files for setup questions and source code for implementation questions.
- **Grounded Answers with Citations** — every answer cites the exact file and line range it drew from, so you can verify and explore further.
- **Markdown Code Formatting** — AI responses render with syntax-highlighted code blocks in the chat UI.
- **Zero Hallucinations** — the LLM is strictly grounded to retrieved context and real repository metadata.

---

## 🏗️ Architecture

```
GitHub URL
    │
    ▼
Git Clone (GitPython)
    │
    ▼
Code Parser & Chunker          ← Walks repo, filters 15+ languages,
(parser_service.py)              splits into 100-line chunks with
                                 tracked file paths & line numbers
    │
    ▼
Sentence Transformers          ← Lightweight 80MB model running on
(all-MiniLM-L6-v2 on MPS)       Apple Silicon GPU — encodes 100+
                                 chunks in ~0.8 seconds
    │
    ▼
MongoDB Atlas (Vector Store)   ← Bulk-writes all 384-dimensional
                                 vectors in a single round-trip
    │
    ▼
User Question
    │
    ├── Embed question (local GPU, ~5ms)
    │
    ├── $vectorSearch (MongoDB Atlas)  ← Top-k candidates retrieved
    │
    ├── Intent Re-ranking              ← Boosts docs/source based on query type
    │
    └── Gemini 2.5 Flash (Cloud LLM)  ← Generates grounded answer with citations
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 8, Tailwind CSS v4, Lucide React, React-Markdown |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` on Apple Silicon GPU (`mps:0`) |
| **Vector Database** | MongoDB Atlas with `$vectorSearch` (384 dimensions) |
| **LLM / Chat** | Google Gemini `gemini-2.5-flash` (cloud API) |
| **Code Parsing** | GitPython, custom line-based chunker |

---

## 📁 Project Structure

```
codebase-rag/
├── frontend/                          # Vite + React single-page app
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatMessage.jsx        # Renders assistant messages with Markdown
│   │   │   ├── ChatWindow.jsx         # Message thread + input box
│   │   │   ├── Header.jsx             # App header with reset
│   │   │   ├── ProcessingStatus.jsx   # Ingestion step tracker
│   │   │   ├── RepositoryInput.jsx    # GitHub URL input form
│   │   │   ├── SourceCard.jsx         # Cited source file + line range badge
│   │   │   └── EmptyState.jsx         # Empty chat placeholder
│   │   ├── services/
│   │   │   └── api.js                 # Centralized FastAPI client
│   │   ├── App.jsx                    # Multi-stage app flow: Input → Processing → Chat
│   │   └── index.css                  # Global styles & design tokens
│   └── package.json
│
└── server/                            # FastAPI Python backend
    ├── app/
    │   ├── database/
    │   │   └── mongodb.py             # MongoDB Atlas connection & collections
    │   ├── models/                    # Pydantic request/response schemas
    │   │   ├── repository.py          # RepositoryRequest (github_url)
    │   │   ├── search.py              # SearchRequest (query, limit)
    │   │   └── chat.py                # ChatRequest (repository_id, question)
    │   ├── routes/                    # FastAPI API routers
    │   │   ├── repository.py          # POST /api/repositories/ingest + /embed
    │   │   ├── search.py              # POST /api/search
    │   │   └── chat.py                # POST /api/chat
    │   ├── services/                  # Core business logic
    │   │   ├── github_service.py      # Git clone via GitPython
    │   │   ├── parser_service.py      # File discovery + 100-line chunking
    │   │   ├── embedding_service.py   # SentenceTransformer + bulk_write
    │   │   ├── search_service.py      # $vectorSearch + intent re-ranking
    │   │   └── chat_service.py        # RAG prompt + Gemini 2.5 Flash
    │   └── main.py                    # FastAPI app entry point + CORS
    ├── temp_repositories/             # Temporary clone directory (auto-cleaned)
    ├── test_embedding.py              # Embedding smoke test
    └── requirements.txt
```

---

## ⚙️ Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB Atlas** account with a cluster ([free tier](https://www.mongodb.com/cloud/atlas/register) works)
- **Google AI Studio API Key** — free at [aistudio.google.com](https://aistudio.google.com/) (no credit card required)

---

## 🚀 Setup & Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/rithika88/codebase-rag.git
cd codebase-rag
```

### 2. MongoDB Atlas: Create a Vector Search Index

In your MongoDB Atlas cluster, on the `code_chunks` collection, create a Vector Search Index:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "repository_id"
    }
  ]
}
```

Name the index `vector_index`.

### 3. Backend Setup

```bash
cd server

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `server/.env`:

```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=codebase-rag
GEMINI_API_KEY=your_google_ai_studio_key_here
```

Start the backend:

```bash
# Use --reload-dir app to avoid hot-reload scanning venv (prevents MacBook heating)
./venv/bin/uvicorn app.main:app --reload --reload-dir app --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔄 How It Works

### Step 1 — Ingest a Repository
1. Paste any public GitHub URL (e.g. `https://github.com/pallets/flask`).
2. The backend clones the repo, walks it (skipping `node_modules`, `venv`, build dirs, lock files), and splits every source file into ~100-line chunks.
3. Each chunk is stored in MongoDB with its file path, start line, and end line.
4. After chunking, the cloned directory is **automatically deleted** from disk.

### Step 2 — Generate Embeddings
1. All chunks are passed through `all-MiniLM-L6-v2` running on your local GPU (Apple Silicon `mps:0`).
2. Encodes 100+ chunks in **~0.8 seconds**.
3. All 384-dimensional vectors are written to MongoDB Atlas in a **single `bulk_write` call**.

### Step 3 — Ask Questions
1. Your question is embedded locally in **~5 milliseconds**.
2. MongoDB Atlas `$vectorSearch` retrieves the top-k most semantically similar chunks.
3. An intent-detection pass re-ranks results (boosting documentation for setup questions, source code for implementation questions).
4. Retrieved chunks + repository metadata are assembled into a grounded prompt for **Gemini 2.5 Flash**.
5. The AI generates an answer citing exact files and line numbers, rendered as Markdown in the chat.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check, confirms DB connection |
| `POST` | `/api/repositories/ingest` | Clone, parse & chunk a GitHub repository |
| `POST` | `/api/repositories/{id}/embed` | Generate & store embeddings for a repository |
| `POST` | `/api/search` | Semantic search over repository chunks |
| `POST` | `/api/chat` | Ask a question, get a grounded answer with sources |

Full interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs) when the backend is running.

---

## 🧠 Supported Languages

`.py` `.js` `.jsx` `.ts` `.tsx` `.java` `.kt` `.go` `.rs` `.c` `.cpp` `.h` `.hpp` `.php` `.rb` `.swift` `.html` `.css` `.scss` `.sql` `.sh` `.yaml` `.yml` `.json` `.md`

Also indexes: `README`, `Dockerfile`, `Makefile`, `LICENSE`

---

## 💡 Tips

- **MacBook Performance**: Always start the backend with `--reload-dir app` to prevent Uvicorn's file watcher from scanning `venv/` and overheating your Mac.
- **Suppressing HF Warning**: The `You are sending unauthenticated requests to the HF Hub` warning is harmless — the model is already cached locally and loads in milliseconds. No download occurs.
- **Large Repositories**: Repos with 1,000+ files embed in seconds thanks to the local GPU with no API rate limits.
