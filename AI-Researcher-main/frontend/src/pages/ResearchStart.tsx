import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startResearch } from "../api/research";
import type { ModeEnum, ResearchRequest } from "../api/types";

export default function ResearchStart() {
  const navigate = useNavigate();

  const [mode, setMode] = useState<ModeEnum>("detailed_idea");
  const [input, setInput] = useState("");
  const [references, setReferences] = useState("");
  const [category, setCategory] = useState("vq");
  const [instanceId, setInstanceId] = useState("one_layer_vq");
  const [taskLevel, setTaskLevel] = useState<"task1" | "task2">("task1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit =
    (mode === "detailed_idea" && input.trim().length > 0) ||
    (mode === "reference_based" && references.trim().length > 0);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!canSubmit) {
      setError("Please provide required fields for the selected mode.");
      return;
    }

    const payload: ResearchRequest = {
      mode,
      category,
      instance_id: instanceId,
      task_level: taskLevel,
      ...(mode === "detailed_idea"
        ? { input: input.trim() }
        : { references: references.split("\n").map((s) => s.trim()).filter(Boolean) }),
    };

    try {
      setLoading(true);
      const res = await startResearch(payload);
      navigate(`/research/${encodeURIComponent(res.job_id)}`);
    } catch (err: any) {
      setError(err?.message || "Failed to start research");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Start Research</h1>
        <p className="text-sm text-muted">
          Progressive disclosure: only fields relevant to the chosen mode are shown.
        </p>
      </header>

      <form onSubmit={onSubmit} className="space-y-5 max-w-2xl">
        {error && (
          <div className="rounded-md border border-red-300/60 bg-red-50 text-red-800 px-3 py-2 text-sm">
            {error}
          </div>
        )}

        <div className="card space-y-3">
          <label className="block text-sm font-medium">Mode</label>
          <div className="flex gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="mode"
                value="detailed_idea"
                checked={mode === "detailed_idea"}
                onChange={() => setMode("detailed_idea")}
              />
              Detailed Idea
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="mode"
                value="reference_based"
                checked={mode === "reference_based"}
                onChange={() => setMode("reference_based")}
              />
              Reference-Based
            </label>
          </div>
        </div>

        {mode === "detailed_idea" && (
          <div className="card space-y-2">
            <label className="block text-sm font-medium">Idea</label>
            <textarea
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-3"
              rows={5}
              placeholder="Describe your idea..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <p className="text-xs text-muted">
              Aim for clarity. The agent will expand and plan from this idea.
            </p>
          </div>
        )}

        {mode === "reference_based" && (
          <div className="card space-y-2">
            <label className="block text-sm font-medium">References (one per line)</label>
            <textarea
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-3"
              rows={5}
              placeholder="e.g. Neural discrete representation learning&#10;Straightening out the straight-through estimator"
              value={references}
              onChange={(e) => setReferences(e.target.value)}
            />
            <p className="text-xs text-muted">
              Provide titles/identifiers. The agent will synthesize from these sources.
            </p>
          </div>
        )}

        <div className="grid sm:grid-cols-3 gap-4">
          <div className="card space-y-2">
            <label className="block text-sm font-medium">Category</label>
            <select
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
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

          <div className="card space-y-2">
            <label className="block text-sm font-medium">Task Level</label>
            <select
              className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2"
              value={taskLevel}
              onChange={(e) => setTaskLevel(e.target.value as "task1" | "task2")}
            >
              <option value="task1">task1</option>
              <option value="task2">task2</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={loading || !canSubmit}
            className="disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Starting..." : "Start Research"}
          </button>
          <span className="text-xs text-muted">
            You can monitor logs live once the job is created.
          </span>
        </div>
      </form>
    </div>
  );
}
