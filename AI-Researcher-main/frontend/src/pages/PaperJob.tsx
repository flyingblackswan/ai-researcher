import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getPaperStatus, getPaperPdf } from "../api/paper";
import type { JobStatus } from "../api/types";
import { connectLogs, type LogEvent } from "../lib/ws";

export default function PaperJob() {
  const { jobId } = useParams<{ jobId: string }>();
  const [events, setEvents] = useState<LogEvent[]>([]);
  const [wsError, setWsError] = useState<string | null>(null);

  const {
    data: statusData,
    isFetching: statusFetching,
  } = useQuery({
    queryKey: ["paper-status", jobId],
    queryFn: () => getPaperStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: 3000,
  });

  const {
    data: pdfData,
    refetch: refetchPdf,
    isFetching: pdfFetching,
  } = useQuery({
    queryKey: ["paper-pdf", jobId],
    queryFn: () => getPaperPdf(jobId!),
    enabled: !!jobId && (statusData?.status === "completed" || statusData?.status === "error"),
  });

  useEffect(() => {
    if (!jobId) return;
    const handle = connectLogs(
      "paper",
      jobId,
      (e) => {
        setEvents((prev) => {
          const next = [...prev, e];
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
      refetchPdf();
    }
  }, [statusData?.status, refetchPdf]);

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

  const pdfPath = pdfData?.pdf ?? pdfData?.artifacts?.pdf;

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Paper Job</h1>
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
            <h2 className="text-sm font-semibold mb-3">PDF</h2>
            {pdfFetching && <div className="text-sm text-muted">Loading PDF path...</div>}
            {!pdfFetching && !pdfPath && (
              <div className="text-sm text-muted">PDF path will appear when available.</div>
            )}
            {pdfPath && (
              <div className="space-y-2">
                <div className="text-sm">Path:</div>
                <pre className="text-xs bg-neutral-950/80 text-neutral-100 p-3 rounded-md overflow-auto">
                  {pdfPath}
                </pre>
                {/* If the backend serves the PDF, render a download link; otherwise display the path for manual access */}
                <a
                  href={typeof pdfPath === "string" ? pdfPath : "#"}
                  className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Open PDF
                </a>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
