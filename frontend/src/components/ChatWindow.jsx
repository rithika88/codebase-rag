import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import ChatMessage from "./ChatMessage";
import EmptyState from "./EmptyState";

export default function ChatWindow({ messages, onSend, isSending }) {
  const [question, setQuestion] = useState("");
  const [showEmptyWarning, setShowEmptyWarning] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setShowEmptyWarning(true);
      return;
    }
    setShowEmptyWarning(false);
    onSend(trimmed);
    setQuestion("");
  }

  function handlePick(example) {
    onSend(example);
  }

  return (
    <div className="flex h-[520px] flex-col overflow-hidden rounded-md border border-border bg-surface">
      <div ref={scrollRef} className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <EmptyState onPick={handlePick} />
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t border-border-soft p-3"
      >
        <input
          type="text"
          value={question}
          disabled={isSending}
          onChange={(e) => {
            setQuestion(e.target.value);
            if (showEmptyWarning) setShowEmptyWarning(false);
          }}
          placeholder="Ask a question about this repository..."
          className="flex-1 rounded-md border border-border bg-ink px-3 py-2 text-sm text-hi placeholder:text-faint outline-none transition-colors focus:border-accent-dim disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isSending}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-accent text-ink transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
          aria-label="Send question"
        >
          <Send size={15} strokeWidth={2.5} />
        </button>
      </form>
      {showEmptyWarning && (
        <p className="px-3 pb-2 text-xs text-danger">
          Type a question before sending.
        </p>
      )}
    </div>
  );
}
