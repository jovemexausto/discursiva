"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSubmission, type Submission } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { ScoreRing } from "@/components/ScoreRing";

export default function SubmissionDetail({ params }: { params: { id: string } }) {
  const [sub, setSub] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const fetchDetail = async () => {
      try {
        const data = await getSubmission(params.id);
        setSub(data);
        setError(null);

        // Polling para atualizar a submissão caso ainda esteja sendo processada
        if (data.status === "PENDING" || data.status === "PROCESSING") {
          timeoutId = setTimeout(fetchDetail, 3000);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] fade-in">
        <div className="w-8 h-8 rounded-full border-[3px] border-indigo-100 border-t-indigo-500 animate-spin" />
      </div>
    );
  }

  if (error || !sub) {
    return (
      <div className="text-center py-12 fade-in">
        <div className="mx-auto h-12 w-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
          <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao carregar</h3>
        <p className="text-gray-500 mb-6">{error || "Submissão não encontrada"}</p>
        <Link href="/submissions" className="btn-primary inline-flex">
          Voltar para submissões
        </Link>
      </div>
    );
  }

  const date = new Date(sub.created_at).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="space-y-8 fade-in pb-12">
      <div>
        <Link href="/submissions" className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors mb-6">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Voltar
        </Link>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 truncate flex items-center gap-3">
          Submissão
          <span className="text-xl font-mono text-gray-400 font-normal">#{sub.id.split("-")[0]}</span>
        </h1>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1.5">ID Original</h3>
            <p className="font-mono text-sm text-gray-900 bg-white border border-gray-200 rounded-lg px-3 py-2 break-all shadow-sm">
              {sub.id}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1.5">Aluno</h3>
            <p className="text-sm text-gray-900 font-medium">
              {sub.student_id}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1.5">Data de envio</h3>
            <p className="text-sm text-gray-900">
              {date}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1.5">Chave S3</h3>
            <p className="font-mono text-xs text-gray-600 break-all">
              {sub.s3_key}
            </p>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-3">Status da Correção</h3>
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="scale-125 mb-2 transition-all duration-500">
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
              <StatusBadge status={sub.status} />
              {sub.score !== null && (
                <p className="text-sm text-gray-500 mt-2 fade-in">
                  Nota final: <strong>{sub.score}%</strong>
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
