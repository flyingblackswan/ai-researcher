import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getConfig, setConfig, bulkSetConfig } from "../api/config";
import type { ConfigItem, ConfigListedItem } from "../api/types";

export default function ConfigPage() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["config-list"],
    queryFn: getConfig,
  });

  const [filter, setFilter] = useState("");
  const [editing, setEditing] = useState<ConfigItem | null>(null);
  const [bulkText, setBulkText] = useState("");

  const setOne = useMutation({
    mutationFn: (item: ConfigItem) => setConfig(item),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["config-list"] }),
  });

  const bulkSet = useMutation({
    mutationFn: (items: ConfigItem[]) => bulkSetConfig(items),
    onSuccess: () => {
      setBulkText("");
      qc.invalidateQueries({ queryKey: ["config-list"] });
    },
  });

  const items = data?.items ?? [];
  const filtered = useMemo(() => {
    const f = filter.toLowerCase().trim();
    if (!f) return items;
    return items.filter((i) => i.key.toLowerCase().includes(f) || i.source.toLowerCase().includes(f));
  }, [items, filter]);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Configuration</h1>
        <p className="text-sm text-muted">View environment variables and update values. Sensitive keys may be masked in the UI.</p>
      </header>

      <div className="card space-y-3">
        <div className="flex gap-3 items-center">
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by key or source..."
            className="w-full sm:w-80 rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2 text-sm"
          />
          <button
            onClick={() => qc.invalidateQueries({ queryKey: ["config-list"] })}
            className="text-sm"
          >
            Refresh
          </button>
        </div>
        {isLoading && <div className="text-sm text-muted">Loading configuration…</div>}
        {error && <div className="text-sm text-danger">Failed to load configuration</div>}

        {!isLoading && !error && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b border-neutral-200/60 dark:border-neutral-800/60">
                  <th className="py-2 pr-4">Key</th>
                  <th className="py-2 pr-4">Value</th>
                  <th className="py-2 pr-4">Source</th>
                  <th className="py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((i) => (
                  <Row
                    key={i.key}
                    item={i}
                    onEdit={() => setEditing({ key: i.key, value: i.value })}
                  />
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <div className="text-sm text-muted py-3">No items match your filter.</div>
            )}
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card space-y-3">
          <h2 className="text-sm font-semibold">Edit Single</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!editing || !editing.key.trim()) return;
              setOne.mutate(editing);
            }}
            className="space-y-3"
          >
            <div className="grid sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium">Key</label>
                <input
                  value={editing?.key ?? ""}
                  onChange={(e) => setEditing((prev) => ({ key: e.target.value, value: prev?.value ?? "" }))}
                  placeholder="KEY"
                  className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium">Value</label>
                <input
                  value={editing?.value ?? ""}
                  onChange={(e) => setEditing((prev) => ({ key: prev?.key ?? "", value: e.target.value }))}
                  placeholder="value"
                  className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-2 text-sm"
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button type="submit" disabled={setOne.isPending} className="text-sm disabled:opacity-50">
                {setOne.isPending ? "Saving…" : "Save"}
              </button>
              <button type="button" onClick={() => setEditing({ key: "", value: "" })} className="text-sm">
                Clear
              </button>
              {setOne.isSuccess && <span className="text-xs text-primary">Saved.</span>}
              {setOne.isError && <span className="text-xs text-danger">Failed.</span>}
            </div>
          </form>
        </div>

        <div className="card space-y-3">
          <h2 className="text-sm font-semibold">Bulk Set</h2>
          <p className="text-xs text-muted">
            Enter KEY=VALUE pairs (one per line). Existing keys will be updated; new keys will be created for the API session context.
          </p>
          <textarea
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
            rows={8}
            placeholder={"OPENROUTER_API_KEY=sk-...\nWORKPLACE_NAME=workplace\nCACHE_PATH=cache"}
            className="w-full rounded-md border border-neutral-300/60 dark:border-neutral-700/60 bg-transparent p-3 text-xs font-mono"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                const items: ConfigItem[] = [];
                for (const line of bulkText.split("\n")) {
                  const idx = line.indexOf("=");
                  if (idx <= 0) continue;
                  const key = line.slice(0, idx).trim();
                  const value = line.slice(idx + 1).trim();
                  if (key) items.push({ key, value });
                }
                if (items.length > 0) bulkSet.mutate(items);
              }}
              disabled={bulkSet.isPending}
              className="text-sm disabled:opacity-50"
            >
              {bulkSet.isPending ? "Applying…" : "Apply"}
            </button>
            {bulkSet.isSuccess && <span className="text-xs text-primary">Applied.</span>}
            {bulkSet.isError && <span className="text-xs text-danger">Failed.</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({ item, onEdit }: { item: ConfigListedItem; onEdit: () => void }) {
  const masked =
    item.key.toLowerCase().includes("key") ||
    item.key.toLowerCase().includes("token") ||
    item.key.toLowerCase().includes("secret");

  return (
    <tr className="border-b border-neutral-200/60 dark:border-neutral-800/60">
      <td className="py-2 pr-4 font-mono text-xs">{item.key}</td>
      <td className="py-2 pr-4">
        <code className="text-xs">
          {masked ? "••••••••" : item.value}
        </code>
      </td>
      <td className="py-2 pr-4 text-xs text-muted">{item.source}</td>
      <td className="py-2">
        <button onClick={onEdit} className="text-xs">Edit</button>
      </td>
    </tr>
  );
}
