import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getResearchStatus, getResearchArtifacts } from "../api/research";
import type { JobStatus } from "../api/types";
import { connectLogs, type LogEvent } from "../lib/ws";

export default function ResearchJob() {
  const { jobId } = useParams<{ jobId: string }>();
  const [events, setEvents] = useState<LogEvent[]>([]);
  const [wsError, setWsError] = useState<string | null>(null);

  const {
    data: statusData,
    refetch: refetchStatus,
    isFetching: statusFetching,
  } = useQuery({
    queryKey: ["research-status", jobId],
    queryFn: () => getResearchStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: 3000,
  });

  const {
    data: artifactsData,
    refetch: refetchArtifacts,
    isFetching: artifactsFetching,
  } = useQuery({
    queryKey: ["research-artifacts", jobId],
    queryFn: () => getResearchArtifacts(jobId!),
    enabled: !!jobId && (statusData?.status === "completed" || statusData?.status === "error"),
  });

  useEffect(() => {
    if (!jobId) return;
    const handle = connectLogs(
      "research",
      jobId,
      (e) => {
        setEvents((prev) => {
          const next = [...prev, e];
          // cap in memory for sustainability
          if (next.length > 1000) next.shift();
          return next;
        });
      },
      (err) => setWsError(String(err))
    );
    return () => handle.close();
  }, [jobId]);

  useEffect(() => {
    if (statusData?.status === "completed" || statusData?.status === "error") {
      refetchArtifacts();
    }
  }, [statusData?.status, refetchArtifacts]);

  const status: JobStatus | undefined = statusData?.status as JobStatus | undefined;

  const statusColor = useMemo(() => {
    switch (status) {
      case "queued":
        return "bg-muted/20 text-muted";
      case "running":
        return "bg-info/10 text-info";
      case "completed":
        return "bg-primary/10 text-primary";
      case "error":
        return "bg-danger/10 text-danger";
      default:
        return "bg-muted/10 text-muted";
    }
  }, [status]);

  const artifacts = useMemo(() => artifactsData?.artifacts as any, [artifactsData]);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Research Job</h1>
        <p className="text-sm text-muted">Job ID: <code className="px-1 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800">{jobId}</code></p>
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="space-y-3">
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded ${statusColor}`}>
            <span className="h-2 w-2 rounded-full bg-current"></span>
            <span className="text-sm font-medium">{status ?? "loading..."}</span>
            {statusFetching && <span className="text-xs opacity-70">(updating)</span>}
          </div>

          {wsError && (
            <div className="rounded-md border border-yellow-300/60 bg-yellow-50 text-yellow-900 px-3 py-2 text-xs">
              Log stream issue: {wsError}
            </div>
          )}

          <div className="card">
            <h2 className="text-sm font-semibold mb-3">Live Logs</h2>
            <div className="h-96 overflow-auto text-xs font-mono leading-relaxed">
              {events.length === 0 ? (
                <div className="text-muted">No events yet...</div>
              ) : (
                events.map((e, idx) => (
                  <div key={idx} className="whitespace-pre-wrap">
                    <span className="text-muted">[{e.timestamp}]</span> {e.message}
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <div className="card">
            <h2 className="text-sm font-semibold mb-3">Artifacts</h2>
            {artifactsFetching && <div className="text-sm text-muted">Loading artifacts...</div>}
            {!artifactsFetching && !artifactsData && (
              <div className="text-sm text-muted">Artifacts will appear here when available.</div>
            )}
            {artifactsData && (
              <div className="space-y-3">
                {artifacts && (artifacts.summary || artifacts.mode) && (
                  <div className="rounded-md border p-3">
                    <div className="text-sm font-medium">{artifacts.summary || "Result"}</div>
                    {"mode" in artifacts && (
                      <div className="text-xs text-muted">Mode: {String(artifacts.mode)}</div>
                    )}
                  </div>
                )}
                {artifacts?.paths && typeof artifacts.paths === "object" && (
                  <div className="rounded-md border p-3">
                    <div className="text-sm font-medium mb-2">Paths</div>
                    <ul className="text-xs space-y-1">
                      {Object.entries(artifacts.paths as Record<string, unknown>).map(([k, v]) => (
                        <li key={k}>
                          <span className="text-muted">{k}:</span>{" "}
                          <code className="break-all">{String(v)}</code>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <pre className="text-xs bg-neutral-950/80 text-neutral-100 p-3 rounded-md overflow-auto">
                  {JSON.stringify(artifactsData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
