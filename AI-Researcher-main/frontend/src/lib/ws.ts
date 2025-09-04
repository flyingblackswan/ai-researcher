import { ZodError, z } from "zod";
import { getWsBase } from "../api/client";

const ZLogEvent = z.object({
  type: z.enum(["log", "status", "error"]),
  timestamp: z.string(),
  message: z.string(),
  tool: z.string().optional(),
  job_id: z.string().optional(),
});

export type LogEvent = z.infer<typeof ZLogEvent>;

export type JobType = "research" | "paper";

export interface WSHandle {
  close: () => void;
}

/**
 * Connect to backend log stream with basic auto-reconnect.
 * Functional ornament: reconnection is exponential up to a small cap to avoid jitter.
 */
export function connectLogs(
  jobType: JobType,
  jobId: string,
  onEvent: (e: LogEvent) => void,
  onError?: (err: unknown) => void
): WSHandle {
  let ws: WebSocket | null = null;
  let closed = false;
  let attempts = 0;
  const wsBase = getWsBase();
  const url = `${wsBase}/api/v1/logs/${encodeURIComponent(jobType)}/${encodeURIComponent(jobId)}`;

  const connect = () => {
    if (closed) return;

    try {
      ws = new WebSocket(url);
    } catch (e) {
      onError?.(e);
      scheduleReconnect();
      return;
    }

    ws.onopen = () => {
      attempts = 0;
    };

    ws.onmessage = (ev) => {
      // Each message should be a JSON line, but be resilient to unexpected formats.
      const ts = new Date().toISOString();

      const acceptCoerced = (obj: any) => {
        // Try to coerce loosely to our shape before giving up
        const maybe = {
          type: typeof obj?.type === "string" && ["log","status","error"].includes(obj.type) ? obj.type : "log",
          timestamp: typeof obj?.timestamp === "string" ? obj.timestamp : ts,
          message: typeof obj?.message === "string" ? obj.message : (typeof obj === "string" ? obj : JSON.stringify(obj)),
          job_id: typeof obj?.job_id === "string" ? obj.job_id : undefined,
          tool: typeof obj?.tool === "string" ? obj.tool : undefined,
        };
        try {
          const parsed = ZLogEvent.parse(maybe);
          onEvent(parsed);
        } catch (zerr) {
          // As a final fallback, emit as plain log event so UI never breaks
          onEvent({ type: "log", timestamp: ts, message: typeof ev.data === "string" ? ev.data : String(ev.data) });
        }
      };

      try {
        const data = JSON.parse(ev.data);
        try {
          const parsed = ZLogEvent.parse(data);
          onEvent(parsed);
        } catch {
          acceptCoerced(data);
        }
      } catch {
        // Not JSON - forward as a plain log line
        onEvent({ type: "log", timestamp: ts, message: typeof ev.data === "string" ? ev.data : String(ev.data) });
      }
    };

    ws.onerror = (ev) => {
      onError?.(ev);
    };

    ws.onclose = () => {
      if (!closed) scheduleReconnect();
    };
  };

  const scheduleReconnect = () => {
    attempts += 1;
    const delay = Math.min(1000 * Math.pow(2, attempts), 8000); // cap at 8s
    setTimeout(() => {
      if (!closed) connect();
    }, delay);
  };

  connect();

  return {
    close: () => {
      closed = true;
      try {
        ws?.close();
      } catch {
        /* ignore */
      }
    },
  };
}
