import { useState, useCallback } from "react";
import Header from "./components/Header";
import RepositoryInput from "./components/RepositoryInput";
import ProcessingStatus from "./components/ProcessingStatus";
import ChatWindow from "./components/ChatWindow";
import { ingestRepository, embedRepository, askQuestion } from "./services/api";

// App stages
const STAGE = {
  INPUT: "input",
  PROCESSING: "processing",
  READY: "ready",
};

function repoNameFromUrl(url) {
  const cleaned = url.trim().replace(/\.git\/?$/, "").replace(/\/$/, "");
  const parts = cleaned.split("/");
  return parts[parts.length - 1] || cleaned;
}

function initialSteps() {
  return [
    { key: "clone", label: "Cloning repository", state: "pending" },
    { key: "parse", label: "Parsing files", state: "pending" },
    { key: "chunk", label: "Creating code chunks", state: "pending" },
    { key: "embed", label: "Generating embeddings", state: "pending" },
    { key: "ready", label: "Repository ready", state: "pending" },
  ];
}

export default function App() {
  const [stage, setStage] = useState(STAGE.INPUT);
  const [inputError, setInputError] = useState("");
  const [steps, setSteps] = useState(initialSteps());
  const [repo, setRepo] = useState(null); // { id, name, githubUrl, filesFound, chunksCreated }
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);

  const updateStep = useCallback((key, patch) => {
    setSteps((prev) =>
      prev.map((s) => (s.key === key ? { ...s, ...patch } : s))
    );
  }, []);

  async function handleAnalyze(githubUrl) {
    setInputError("");
    setSteps(initialSteps());
    setStage(STAGE.PROCESSING);

    updateStep("clone", { state: "active" });
    updateStep("parse", { state: "active" });
    updateStep("chunk", { state: "active" });

    let ingestResult;
    try {
      ingestResult = await ingestRepository(githubUrl);
    } catch (err) {
      updateStep("clone", {
        state: "error",
        label: "Repository ingestion failed",
        detail:
          err.status === 0
            ? "Can't reach the backend. Please check your connection and try again."
            : "Unable to clone repository. Please check the GitHub URL.",
      });
      updateStep("parse", { state: "pending" });
      updateStep("chunk", { state: "pending" });
      setStage(STAGE.INPUT);
      setInputError(
        err.status === 0
          ? "Can't reach the backend. Is the FastAPI server running?"
          : "Unable to clone repository. Please check the GitHub URL."
      );
      return;
    }

    updateStep("clone", { state: "done" });
    updateStep("parse", { state: "done" });
    updateStep("chunk", {
      state: "done",
      detail: `${ingestResult.files_found} files · ${ingestResult.chunks_created} chunks`,
    });
    updateStep("embed", { state: "active" });

    try {
      await embedRepository(ingestResult.repository_id);
    } catch (err) {
      updateStep("embed", {
        state: "error",
        label: "Unable to generate embeddings",
        detail: err.message,
      });
      setStage(STAGE.INPUT);
      setInputError("Unable to generate embeddings. Please try again.");
      return;
    }

    updateStep("embed", { state: "done" });
    updateStep("ready", { state: "done" });

    setRepo({
      id: ingestResult.repository_id,
      name: repoNameFromUrl(githubUrl),
      githubUrl,
      filesFound: ingestResult.files_found,
      chunksCreated: ingestResult.chunks_created,
    });
    setMessages([]);
    setStage(STAGE.READY);
  }

  async function handleSend(question) {
    const userMessage = { id: crypto.randomUUID(), role: "user", content: question };
    const pendingId = crypto.randomUUID();
    const pendingMessage = { id: pendingId, role: "assistant", pending: true };

    setMessages((prev) => [...prev, userMessage, pendingMessage]);
    setIsSending(true);

    try {
      const result = await askQuestion(repo.id, question);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { ...m, pending: false, content: result.answer, sources: result.sources }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                ...m,
                pending: false,
                error: true,
                content:
                  err.status === 0
                    ? "Can't reach the backend. Please check your connection."
                    : "Something went wrong while generating the answer.",
              }
            : m
        )
      );
    } finally {
      setIsSending(false);
    }
  }

  function handleReset() {
    setStage(STAGE.INPUT);
    setInputError("");
    setSteps(initialSteps());
    setRepo(null);
    setMessages([]);
    setIsSending(false);
  }

  return (
    <div className="mx-auto flex min-h-full max-w-2xl flex-col gap-8 px-5 py-10 sm:px-6">
      <Header onReset={handleReset} showReset={stage !== STAGE.INPUT} />

      {stage === STAGE.INPUT && (
        <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-5">
          <RepositoryInput onAnalyze={handleAnalyze} isBusy={false} error={inputError} />
        </section>
      )}

      {stage === STAGE.PROCESSING && <ProcessingStatus steps={steps} />}

      {stage === STAGE.READY && repo && (
        <>
          <section className="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3">
            <div>
              <p className="font-mono text-sm font-semibold text-hi">{repo.name}</p>
              <p className="mt-0.5 text-xs text-lo">
                {repo.filesFound} files · {repo.chunksCreated} chunks
              </p>
            </div>
            <span className="flex items-center gap-1.5 rounded-full border border-accent-dim/40 bg-accent/10 px-2.5 py-1 text-[0.7rem] font-semibold text-accent">
              Ready
            </span>
          </section>

          <ChatWindow messages={messages} onSend={handleSend} isSending={isSending} />
        </>
      )}
    </div>
  );
}
