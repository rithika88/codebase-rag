import { TerminalSquare } from "lucide-react";

export default function Header({ onReset, showReset }) {
  return (
    <header className="flex items-center justify-between border-b border-border-soft pb-6">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md border border-border bg-surface text-accent">
          <TerminalSquare size={18} strokeWidth={2} />
        </div>
        <div>
          <h1 className="text-[1.05rem] font-bold leading-tight tracking-tight text-hi">
            Codebase RAG
          </h1>
          <p className="text-[0.8rem] text-lo">
            Understand any GitHub repository with AI
          </p>
        </div>
      </div>

      {showReset && (
        <button
          onClick={onReset}
          className="rounded-md border border-border px-3 py-1.5 font-mono text-xs text-lo transition-colors hover:border-accent-dim hover:text-hi cursor-pointer"
        >
          New repository
        </button>
      )}
    </header>
  );
}
