import { apiFetch } from "./client";
import type { ResearchRequest, JobResponse, StatusResponse } from "./types";

export async function startResearch(payload: ResearchRequest): Promise<JobResponse> {
  return apiFetch<JobResponse>("/api/v1/research/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getResearchStatus(jobId: string): Promise<StatusResponse> {
  return apiFetch<StatusResponse>(`/api/v1/research/${encodeURIComponent(jobId)}/status`);
}

export async function getResearchArtifacts(jobId: string): Promise<{ status: string; artifacts: Record<string, any> }> {
  return apiFetch(`/api/v1/research/${encodeURIComponent(jobId)}/artifacts`);
}
