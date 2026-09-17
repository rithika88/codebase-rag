import { useState } from "react";
import { ArrowRight, GitBranch } from "lucide-react";

const GITHUB_URL_PATTERN =
  /^https?:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+(\.git)?\/?$/;

export function isValidGithubUrl(url) {
  return GITHUB_URL_PATTERN.test(url.trim());
}

export default function RepositoryInput({ onAnalyze, isBusy, error }) {
  const [url, setUrl] = useState("");
  const [touched, setTouched] = useState(false);

  const trimmed = url.trim();
  const showValidationError = touched && trimmed.length > 0 && !isValidGithubUrl(trimmed);

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!trimmed) return;
    if (!isValidGithubUrl(trimmed)) return;
    onAnalyze(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <label
        htmlFor="github-url"
        className="text-xs font-semibold text-lo"
      >
        GitHub repository URL
      </label>

      <div className="flex flex-col gap-2 sm:flex-row">
        <div className="relative flex-1">
          <GitBranch
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-faint"
          />
          <input
            id="github-url"
            type="text"
            inputMode="url"
            autoComplete="off"
            spellCheck={false}
            disabled={isBusy}
            placeholder="https://github.com/username/repository.git"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onBlur={() => setTouched(true)}
            className="w-full rounded-md border border-border bg-surface py-2.5 pl-9 pr-3 font-mono text-sm text-hi placeholder:text-faint outline-none transition-colors focus:border-accent-dim disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={isBusy || !trimmed}
          className="flex shrink-0 items-center justify-center gap-2 rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-ink transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
        >
          Analyze repository
          <ArrowRight size={15} strokeWidth={2.5} />
        </button>
      </div>

      {showValidationError && (
        <p className="text-xs text-danger">
          That doesn't look like a GitHub repository URL. Try
          https://github.com/owner/repo
        </p>
      )}

      {error && <p className="text-xs text-danger">{error}</p>}
    </form>
  );
}
