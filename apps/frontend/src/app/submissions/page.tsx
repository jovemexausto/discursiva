"use client";

import { useState, useEffect, useCallback } from "react";
import { listSubmissions, type Submission } from "@/lib/api";
import { SubmissionCard } from "@/components/SubmissionCard";
import { useLocalStorage } from "@/hooks/useLocalStorage";
export default function SubmissionsPage() {
  const [studentId, setStudentId, isHydrated] = useLocalStorage("studentId", "aluno-1");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [total, setTotal] = useState(0);
  const [doneCount, setDoneCount] = useState(0);
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [page, setPage] = useState(1);
  const limit = 10;

  const fetchSubmissions = useCallback(async () => {
    if (!studentId.trim()) return;
    setLoading(true);
    try {
      const data = await listSubmissions(studentId.trim(), limit, (page - 1) * limit);
      setSubmissions(data.items);
      setTotal(data.total);
      setDoneCount(data.done_count ?? 0);
      setPendingCount(data.pending_count ?? 0);
    } catch {
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  }, [studentId, page]);

  useEffect(() => {
    if (!isHydrated) return;
    
    setInitialLoad(true);
    fetchSubmissions();
    const id = setInterval(fetchSubmissions, 5000);
    return () => clearInterval(id);
  }, [fetchSubmissions, isHydrated]);

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
          ID do aluno
        </label>
        <input
          id="filter-student"
          type="text"
          value={studentId}
          onChange={(e) => {
            setStudentId(e.target.value);
            setPage(1);
          }}
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
          {doneCount > 0 && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm text-gray-600">
                <strong>{doneCount}</strong> corrigidas
              </span>
            </div>
          )}
          {pendingCount > 0 && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
              <span className="text-sm text-indigo-600">
                <strong>{pendingCount}</strong> aguardando
              </span>
            </div>
          )}
          <div className="ml-auto flex items-center gap-3">
            {loading && (
              <span className="text-xs text-gray-400 animate-pulse">
                Atualizando …
              </span>
            )}
            {total > 0 && (
              <span className="text-xs text-gray-400 hidden sm:inline-block">
                Exibindo {Math.min((page - 1) * limit + 1, total)} a {Math.min(page * limit, total)} de {total}
              </span>
            )}
          </div>
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
        <div className="space-y-6">
          <div className="space-y-3">
            {submissions.map((sub, i) => (
              <div key={sub.id} className="slide-up" style={{ animationDelay: `${i * 50}ms` }}>
                <SubmissionCard sub={sub} />
              </div>
            ))}
          </div>

          {total > limit && (
            <div className="flex items-center justify-between pt-6 pb-8 border-t border-gray-100">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
                Anterior
              </button>

              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg font-medium">
                  {page} <span className="text-gray-400 font-normal">/ {Math.ceil(total / limit)}</span>
                </span>
              </div>

              <button
                onClick={() => setPage((p) => (p * limit < total ? p + 1 : p))}
                disabled={page * limit >= total}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Próxima
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
