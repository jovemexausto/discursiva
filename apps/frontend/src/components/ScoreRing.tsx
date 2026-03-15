"use client";

export function ScoreRing({ score }: { score: number }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 10) * circ;
  const color = score >= 7 ? "#16a34a" : score >= 5 ? "#ca8a04" : "#dc2626";

  return (
    <div className="relative inline-flex items-center justify-center w-20 h-20">
      <svg className="-rotate-90" width="80" height="80">
        <circle cx="40" cy="40" r={r} stroke="#e5e7eb" strokeWidth="6" fill="none" />
        <circle
          cx="40" cy="40" r={r}
          stroke={color} strokeWidth="6" fill="none"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <span className="absolute text-lg font-bold" style={{ color }}>
        {score.toFixed(1)}
      </span>
    </div>
  );
}
