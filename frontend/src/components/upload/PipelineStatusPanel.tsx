import { Link } from "@tanstack/react-router";
import { Check, Loader2, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePipelineStatus } from "@/lib/veritas/hooks";

/**
 * Pipeline stages as defined by the backend contract §3.3.
 * The backend returns a single `status` string; we display it as a stepper.
 */
const PIPELINE_STAGES = [
  "extracting",
  "cross_checking",
  "red_teaming",
  "classifying",
  "policy_deciding",
  "done",
] as const;

const STAGE_LABEL: Record<string, string> = {
  extracting: "Extracting",
  cross_checking: "Cross-checking",
  red_teaming: "Red-teaming",
  classifying: "Classifying",
  policy_deciding: "Deciding",
  done: "Done",
};

export function PipelineStatusPanel({ documentId }: { documentId: string }) {
  const { data, isPending } = usePipelineStatus(documentId);

  if (isPending || !data) {
    return (
      <div className="rounded-md border bg-surface p-6">
        <div className="h-3 w-40 animate-pulse rounded bg-muted" />
        <div className="mt-6 grid grid-cols-6 gap-2">
          {PIPELINE_STAGES.map((s) => (
            <div key={s} className="h-10 animate-pulse rounded bg-muted" />
          ))}
        </div>
      </div>
    );
  }

  if (data.status === "error") {
    return (
      <div className="flex items-start gap-3 rounded-md border border-unsupported/30 bg-unsupported-soft p-5 text-sm text-unsupported">
        <TriangleAlert className="mt-0.5 h-4 w-4" aria-hidden />
        <p>{data.error ?? "The pipeline stopped unexpectedly. Upload the document again."}</p>
      </div>
    );
  }

  const currentIndex = PIPELINE_STAGES.indexOf(data.status as typeof PIPELINE_STAGES[number]);
  const pct = data.attributes_total
    ? Math.round((data.attributes_processed / data.attributes_total) * 100)
    : 0;

  return (
    <div className="rounded-md border bg-surface">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
        <div>
          <p className="data-value text-xs text-muted-foreground">{data.document_id}</p>
        </div>
        <span className="data-value text-xs uppercase tracking-[0.16em] text-muted-foreground">
          {data.status === "done" ? "Pipeline complete" : "Pipeline running"}
        </span>
      </div>

      <ol className="grid gap-2 px-5 py-5 sm:grid-cols-3 lg:grid-cols-6">
        {PIPELINE_STAGES.map((stage, i) => {
          const state = i < currentIndex ? "past" : i === currentIndex ? "current" : "future";
          return (
            <li
              key={stage}
              className={cn(
                "flex items-center gap-2 rounded-sm border px-3 py-2 text-xs transition-colors",
                state === "past" && "border-verified/30 bg-verified-soft text-verified",
                state === "current" && "border-primary/40 bg-accent text-accent-foreground",
                state === "future" && "text-muted-foreground",
              )}
            >
              {state === "past" ? (
                <Check className="h-3.5 w-3.5" aria-hidden />
              ) : state === "current" && data.status !== "done" ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
              ) : (
                <span className="data-value w-3.5 text-center">{i + 1}</span>
              )}
              {STAGE_LABEL[stage]}
            </li>
          );
        })}
      </ol>

      <div className="border-t px-5 py-4">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Attributes processed</span>
          <span className="data-value">
            {data.attributes_processed} / {data.attributes_total}
          </span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {data.status === "done" ? (
        <div className="border-t px-5 py-4">
          <Link
            to="/catalog"
            className="inline-flex rounded-sm bg-primary px-3 py-2 text-xs font-medium text-primary-foreground hover:opacity-90"
          >
            View results in catalog
          </Link>
        </div>
      ) : null}
    </div>
  );
}
