import { apiFetch } from "./client";
import type { ConfigItem, ConfigListResponse } from "./types";

export async function getConfig(): Promise<ConfigListResponse> {
  return apiFetch<ConfigListResponse>("/api/v1/config");
}

export async function setConfig(item: ConfigItem): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>("/api/v1/config/set", {
    method: "POST",
    body: JSON.stringify(item),
  });
}

export async function bulkSetConfig(items: ConfigItem[]): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>("/api/v1/config/bulk-set", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}
