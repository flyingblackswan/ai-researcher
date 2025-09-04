import { ZodError, z } from "zod";

// Base URL for the backend API
const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:7039";

// Compute WS base by swapping http -> ws
export const getWsBase = () => apiBase.replace(/^http/i, "ws");

export class ApiError extends Error {
  status: number;
  body?: unknown;
  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

// Generic JSON fetch wrapper with sensible defaults and error handling
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const url = `${apiBase}${path}`;
  const headers = new Headers(init.headers || {});
  if (!headers.has("Content-Type") && (init.method || "GET") !== "GET") {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(url, { ...init, headers });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const body = isJson ? await res.json().catch(() => undefined) : await res.text().catch(() => undefined);

  if (!res.ok) {
    const message =
      (isJson && body && (body.message || body.detail)) ||
      `Request failed: ${res.status} ${res.statusText}`;
    throw new ApiError(message, res.status, body);
  }

  return body as T;
}

// Optional: Zod-safe fetch that validates the response against a schema
export async function apiFetchZ<T>(
  path: string,
  schema: z.ZodSchema<T>,
  init: RequestInit = {}
): Promise<T> {
  const data = await apiFetch<unknown>(path, init);
  try {
    return schema.parse(data);
  } catch (e) {
    if (e instanceof ZodError) {
      throw new Error(`Response validation error: ${e.issues.map((i) => i.message).join(", ")}`);
    }
    throw e;
  }
}
