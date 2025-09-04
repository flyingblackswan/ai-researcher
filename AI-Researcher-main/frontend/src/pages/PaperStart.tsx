import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startPaper } from "../api/paper";
import type { PaperRequest } from "../api/types";

export default function PaperStart() {
  const navigate = useNavigate();
  const [researchField, setResearchField] = useState("vq");
  const [instanceId, setInstanceId] = useState("one_layer_vq");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = researchField.trim().length > 0 && instanceId.trim().length > 0;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!canSubmit) {
      setError("Please provide both research field and instance id.");
      return;
    }
    const payload: PaperRequest = {
      research_field: researchField,
      instance_id: instanceId,
    };
    try {
      setLoading(true);
      const res = await startPaper(payload);
      navigate(`/paper/${encodeURIComponent(res.job_id)}`);
    } catch (err: any) {
      setError(err?.message || "Failed to start paper generation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Generate Paper</h1>
        <p className="text-sm text-muted">Generate a paper for a completed research instance.</p>
      </header>

      <form onSubmit={onSubmit} className="space-y-5 max-w-2xl">
        {error && (
          <div className="rounded-md border border-red-300/60 bg-red-50 text-red-800 px-3 py-2 text-sm">
            {error}
          </div>
        )}

        <div className="grid sm:grid-cols-2 gap-4">
          <div className="card space-y-2">
            <label className="block text-sm font-medium">Research Field</label>
            <select
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2"
              value={researchField}
              onChange={(e) => setResearchField(e.target.value)}
            >
              <option value="vq">vq</option>
              <option value="gnn">gnn</option>
              <option value="diffu_flow">diffu_flow</option>
              <option value="reasoning">reasoning</option>
              <option value="recommendation">recommendation</option>
            </select>
          </div>

          <div className="card space-y-2">
            <label className="block text-sm font-medium">Instance ID</label>
            <input
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2"
              value={instanceId}
              onChange={(e) => setInstanceId(e.target.value)}
              placeholder="e.g. one_layer_vq"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={loading || !canSubmit}
            className="disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Starting..." : "Start Paper Generation"}
          </button>
          <span className="text-xs text-muted">You can monitor logs live once the job is created.</span>
        </div>
      </form>
    </div>
  );
}
