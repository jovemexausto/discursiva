"use client";

import { useState } from "react";
import Link from "next/link";
import { createSubmission, type Submission } from "@/lib/api";

export default function SubmitPage() {
  const [studentId, setStudentId] = useState("aluno-1");
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<Submission | null>(null);

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim() || !studentId.trim()) return;
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const sub = await createSubmission(studentId.trim(), text.trim());
      setSuccess(sub);
      setText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Nova submissão
        </h1>
        <p className="mt-1 text-gray-500">
          Envie a resposta discursiva do aluno.
        </p>
      </div>

      {success && (
        <div className="rounded-2xl border border-green-200 bg-green-50 p-5 slide-up">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100">
              <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-green-800">Submissão enviada!</p>
              <p className="mt-1 text-xs text-green-700 font-mono truncate">
                ID: {success.id}
              </p>
              <Link
                href="/submissions"
                className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-green-700 hover:text-green-800 transition-colors"
              >
                Ver submissões
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="student-id" className="block text-sm font-medium text-gray-700 mb-1.5">
            ID do aluno
          </label>
          <input
            id="student-id"
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="ex: aluno-42"
            required
            className="input sm:max-w-xs"
          />
        </div>

        <div>
          <label htmlFor="answer-text" className="block text-sm font-medium text-gray-700 mb-1.5">
            Resposta discursiva
          </label>
          <textarea
            id="answer-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
            placeholder="Digite a resposta do aluno aqui..."
            required
            className="input resize-none"
          />
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-gray-400">{wordCount} palavras</p>
            {wordCount > 0 && wordCount < 10 && (
              <p className="text-xs text-amber-500">Mínimo recomendado: 10 palavras</p>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 rounded-xl bg-red-50 border border-red-200 px-4 py-3">
            <svg className="h-4 w-4 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <button type="submit" disabled={submitting || !text.trim()} className="btn-primary w-full sm:max-w-xs">
          {submitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Enviando...
            </>
          ) : (
            "Enviar para correção"
          )}
        </button>
      </form>
    </div>
  );
}
