import { apiFetch } from "./client";
import type { PaperRequest, JobResponse, StatusResponse } from "./types";

export async function startPaper(payload: PaperRequest): Promise<JobResponse> {
  return apiFetch<JobResponse>("/api/v1/paper/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getPaperStatus(jobId: string): Promise<StatusResponse> {
  return apiFetch<StatusResponse>(`/api/v1/paper/${encodeURIComponent(jobId)}/status`);
}

export async function getPaperPdf(jobId: string): Promise<{ status: string; pdf?: string; artifacts?: Record<string, any> }> {
  return apiFetch(`/api/v1/paper/${encodeURIComponent(jobId)}/pdf`);
}
