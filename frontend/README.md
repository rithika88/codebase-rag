# Codebase RAG — Frontend

The React frontend for the **Codebase RAG Assistant**. Provides the chat UI for ingesting GitHub repositories and asking questions about their code.

## Tech Stack

- **React 19** — UI framework
- **Vite 8** — dev server and build tool
- **Tailwind CSS v4** — utility-first styling with custom design tokens
- **Lucide React** — icons
- **React-Markdown** — renders assistant responses with code block formatting

## Running Locally

```bash
npm install
npm run dev
```

Requires the FastAPI backend running at `http://localhost:8000`.
To configure a different backend URL, set `VITE_API_BASE_URL` in a `.env` file:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Key Components

| File | Purpose |
|---|---|
| `App.jsx` | Top-level state machine: `Input → Processing → Chat` |
| `RepositoryInput.jsx` | GitHub URL form with validation |
| `ProcessingStatus.jsx` | Visual step tracker during ingestion |
| `ChatWindow.jsx` | Message thread + question input |
| `ChatMessage.jsx` | Renders user/assistant messages with Markdown support |
| `SourceCard.jsx` | Displays cited source file and line range |
| `services/api.js` | Centralized HTTP client for all FastAPI calls |
