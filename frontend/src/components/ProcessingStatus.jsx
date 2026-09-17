import { Check, X } from "lucide-react";

// step.state: "done" | "active" | "pending" | "error"
function StepIcon({ state }) {
  if (state === "done") {
    return (
      <span className="flex h-4 w-4 items-center justify-center rounded-full bg-accent/15 text-accent">
        <Check size={11} strokeWidth={3} />
      </span>
    );
  }
  if (state === "error") {
    return (
      <span className="flex h-4 w-4 items-center justify-center rounded-full bg-danger/15 text-danger">
        <X size={11} strokeWidth={3} />
      </span>
    );
  }
  if (state === "active") {
    return (
      <span className="relative flex h-4 w-4 items-center justify-center">
        <span className="pulse-dot h-2 w-2 rounded-full bg-warm" />
      </span>
    );
  }
  return (
    <span className="flex h-4 w-4 items-center justify-center">
      <span className="h-1.5 w-1.5 rounded-full bg-border" />
    </span>
  );
}

export default function ProcessingStatus({ steps, repoLabel }) {
  return (
    <div className="rounded-md border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border-soft px-4 py-2.5">
        <span className="text-xs font-semibold text-lo">
          Repository analysis
        </span>
        {repoLabel && (
          <span className="truncate font-mono text-xs text-faint">
            {repoLabel}
          </span>
        )}
      </div>

      <ul className="flex flex-col gap-3 px-4 py-4">
        {steps.map((step, i) => (
          <li key={step.key} className="flex items-start gap-3">
            <div className="flex flex-col items-center">
              <StepIcon state={step.state} />
              {i < steps.length - 1 && (
                <span className="mt-1 h-4 w-px bg-border" />
              )}
            </div>
            <div className="flex-1 pt-px">
              <p
                className={`font-mono text-[0.83rem] leading-none ${
                  step.state === "pending" ? "text-faint" : "text-hi"
                } ${step.state === "error" ? "text-danger" : ""}`}
              >
                {step.label}
                {step.state === "active" && (
                  <span className="cursor-blink ml-0.5 text-warm">_</span>
                )}
              </p>
              {step.detail && (
                <p className="mt-1 text-xs text-lo">{step.detail}</p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
