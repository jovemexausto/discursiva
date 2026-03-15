import type { Submission } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import { ScoreRing } from "./ScoreRing";

export function SubmissionCard({ sub }: { sub: Submission }) {
  const shortId = sub.id.split("-").slice(0, 2).join("-");
  const date = new Date(sub.created_at).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="card !p-4 group cursor-default">
      <div className="flex items-center gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <StatusBadge status={sub.status} />
            <span className="text-xs text-gray-400">{date}</span>
          </div>
          <p className="text-xs font-mono text-gray-400 truncate group-hover:text-gray-600 transition-colors">
            {shortId}
          </p>
          <p className="text-xs text-gray-400 mt-0.5 truncate">
            <span className="text-gray-300">s3:</span> {sub.s3_key}
          </p>
        </div>
        <div className="shrink-0 transition-transform duration-200 group-hover:scale-105">
          {sub.score !== null ? (
            <ScoreRing score={sub.score} />
          ) : sub.status === "PROCESSING" || sub.status === "PENDING" ? (
            <div className="w-16 h-16 rounded-full border-[3px] border-indigo-100 border-t-indigo-500 animate-spin shadow-sm" />
          ) : (
            <div className="w-16 h-16 rounded-full border-[3px] border-gray-100 flex items-center justify-center text-gray-300 text-sm">
              —
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
