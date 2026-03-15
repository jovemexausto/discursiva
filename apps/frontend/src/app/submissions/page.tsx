"use client";

import { useState, useEffect, useCallback } from "react";
import { listSubmissions, type Submission } from "@/lib/api";
import { SubmissionCard } from "@/components/SubmissionCard";

export default function SubmissionsPage() {
  const [studentId, setStudentId] = useState("aluno-1");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  const fetchSubmissions = useCallback(async () => {
    if (!studentId.trim()) return;
    setLoading(true);
    try {
      const data = await listSubmissions(studentId.trim());
      setSubmissions(data.items);
      setTotal(data.total);
    } catch {
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  }, [studentId]);

  useEffect(() => {
    setInitialLoad(true);
    fetchSubmissions();
    const id = setInterval(fetchSubmissions, 5000);
    return () => clearInterval(id);
  }, [fetchSubmissions]);

  const pending = submissions.filter(
    (s) => s.status === "PENDING" || s.status === "PROCESSING"
  ).length;
  const done = submissions.filter((s) => s.status === "DONE").length;

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Submissões
        </h1>
        <p className="mt-1 text-gray-500">
          Acompanhe o status das correções em tempo real.
        </p>
      </div>

      <div className="flex flex-col items-start gap-1.5">
        <label htmlFor="filter-student" className="pl-1 text-sm font-medium text-gray-700">
          Filtrar por aluno
        </label>
        <input
          id="filter-student"
          type="text"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          placeholder="ex: aluno-42"
          className="input sm:max-w-xs"
        />
      </div>

      {!initialLoad && (
        <div className="flex items-center gap-6 slide-up pl-2">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-gray-400" />
            <span className="text-sm text-gray-600">
              <strong>{total}</strong> total
            </span>
          </div>
          {done > 0 && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm text-gray-600">
                <strong>{done}</strong> corrigidas
              </span>
            </div>
          )}
          {pending > 0 && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
              <span className="text-sm text-indigo-600">
                <strong>{pending}</strong> aguardando
              </span>
            </div>
          )}
          {loading && (
            <span className="ml-auto text-xs text-gray-400 animate-pulse">
              atualizando…
            </span>
          )}
        </div>
      )}

      {initialLoad ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse !p-4">
              <div className="flex items-center gap-4">
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-24" />
                  <div className="h-3 bg-gray-100 rounded w-48" />
                </div>
                <div className="h-16 w-16 rounded-full bg-gray-100" />
              </div>
            </div>
          ))}
        </div>
      ) : submissions.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-300 p-12 text-center">
          <div className="mx-auto h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
            <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9.75m3 0h.008v.008h-.008v-.008zm0 3H9.75m3 0h.008v.008h-.008v-.008zm0 3H9.75m0-6h.008v.008H9.75v-.008zm0 3h.008v.008H9.75v-.008zm0 3h.008v.008H9.75v-.008zM6 6.75h.75m-.75 3h.75m-.75 3h.75m-.75 3h.75m-.75 3h.75m-.75 3h.75" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">
            Nenhuma submissão encontrada para <strong>{studentId}</strong>.
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Faça uma submissão na página &ldquo;Enviar&rdquo; para começar.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {submissions.map((sub, i) => (
            <div key={sub.id} className="slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <SubmissionCard sub={sub} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
