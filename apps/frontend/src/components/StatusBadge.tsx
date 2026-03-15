import type { Status } from "@/lib/api";

const MAP: Record<Status, { label: string; cls: string }> = {
  PENDING:    { label: "Pendente",   cls: "bg-yellow-100 text-yellow-800" },
  PROCESSING: { label: "Corrigindo", cls: "bg-blue-100   text-blue-800 animate-pulse" },
  DONE:       { label: "Corrigido",  cls: "bg-green-100  text-green-800" },
  ERROR:      { label: "Erro",       cls: "bg-red-100    text-red-800" },
};

export function StatusBadge({ status }: { status: Status }) {
  const { label, cls } = MAP[status];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {label}
    </span>
  );
}
