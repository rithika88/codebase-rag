import { Sparkles } from "lucide-react";

const EXAMPLES = [
  "What technologies are used in this project?",
  "Where is the core logic implemented?",
  "How does the frontend communicate with the backend?",
  "Explain the project architecture.",
];

export default function EmptyState({ onPick }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 py-10 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-md border border-border text-accent">
        <Sparkles size={18} />
      </div>
      <p className="text-sm text-lo">Ask anything about your codebase</p>

      <div className="flex w-full max-w-md flex-col gap-2">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            onClick={() => onPick(example)}
            className="rounded-md border border-border-soft px-3 py-2 text-left font-mono text-xs text-lo transition-colors hover:border-accent-dim hover:text-hi cursor-pointer"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
