const BASE = "/api";

export type Status = "PENDING" | "PROCESSING" | "DONE" | "ERROR";

export interface Submission {
  id: string;
  student_id: string;
  s3_key: string;
  status: Status;
  score: number | null;
  created_at: string;
  updated_at: string;
}

export interface SubmissionPage {
  items: Submission[];
  total: number;
  limit: number;
  offset: number;
}

export async function createSubmission(student_id: string, text: string): Promise<Submission> {
  const res = await fetch(`${BASE}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id, text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSubmission(id: string): Promise<Submission> {
  const res = await fetch(`${BASE}/submissions/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listSubmissions(
  student_id: string,
  limit = 20,
  offset = 0,
): Promise<SubmissionPage> {
  const p = new URLSearchParams({ student_id, limit: String(limit), offset: String(offset) });
  const res = await fetch(`${BASE}/submissions?${p}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
