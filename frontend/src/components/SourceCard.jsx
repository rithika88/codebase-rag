import { FileCode2 } from "lucide-react";

export default function SourceCard({ source }) {
  const percent = Math.round((source.score ?? 0) * 100);

  return (
    <div className="flex items-center gap-3 rounded-md border border-border-soft bg-surface px-3 py-2.5">
      <FileCode2 size={15} className="shrink-0 text-lo" />

      <div className="min-w-0 flex-1">
        <p className="truncate font-mono text-xs text-hi">
          {source.file_path}
        </p>
        <p className="font-mono text-[0.7rem] text-faint">
          Lines {source.start_line}–{source.end_line}
        </p>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <div className="h-1 w-12 overflow-hidden rounded-full bg-border-soft">
          <div
            className="h-full rounded-full bg-warm"
            style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
          />
        </div>
        <span className="font-mono text-[0.7rem] text-lo">{percent}%</span>
      </div>
    </div>
  );
}
