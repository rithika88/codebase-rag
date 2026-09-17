import { AlertTriangle } from "lucide-react";
import SourceCard from "./SourceCard";
import ReactMarkdown from "react-markdown";
function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-1">
      <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-lo [animation-delay:0ms]" />
      <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-lo [animation-delay:150ms]" />
      <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-lo [animation-delay:300ms]" />
    </span>
  );
}

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-md border-r-2 border-accent bg-surface px-4 py-2.5">
          <p className="whitespace-pre-wrap text-sm text-hi">
            <ReactMarkdown>
  {message.content}
</ReactMarkdown>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-md border-l-2 border-border bg-transparent px-4 py-2.5">
        {message.pending ? (
          <TypingDots />
        ) : message.error ? (
          <div className="flex items-start gap-2 text-sm text-danger">
            <AlertTriangle size={15} className="mt-0.5 shrink-0" />
            <span>{message.content}</span>
          </div>
        ) : (
          <>
            <div className="text-sm leading-relaxed text-hi [&_pre]:my-2 [&_pre]:p-3 [&_pre]:rounded-md [&_pre]:bg-surface-raised [&_pre]:overflow-x-auto [&_code]:font-mono [&_code]:text-xs [&_code]:text-accent [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:list-decimal [&_ol]:pl-4 [&_p]:my-1.5">
              <ReactMarkdown>
                {message.content}
              </ReactMarkdown>
            </div>

            {message.sources?.length > 0 && (
              <div className="mt-3 flex flex-col gap-1.5">
                <p className="text-[0.7rem] font-semibold text-lo">
                  Retrieved sources
                </p>
                {message.sources.map((source, i) => (
                  <SourceCard key={`${source.file_path}-${i}`} source={source} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
