import { cn } from "@/lib/utils";
import { classificationMeta, policyMeta } from "@/lib/veritas/classification";
import type { Classification, PolicyDecision } from "@/lib/veritas/schemas";

type Props =
  | { classification: Classification; policy?: never; size?: "sm" | "lg"; className?: string }
  | { policy: PolicyDecision; classification?: never; size?: "sm" | "lg"; className?: string };

export function StatusBadge(props: Props) {
  const meta = props.classification ? classificationMeta(props.classification) : policyMeta(props.policy!);
  return (
    <span
      title={meta.description}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border font-medium uppercase tracking-[0.08em]",
        props.size === "lg" ? "px-3 py-1.5 text-xs" : "px-2 py-0.5 text-[10px]",
        meta.className,
        props.className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden />
      {meta.label}
    </span>
  );
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const tone = pct >= 80 ? "bg-verified" : pct >= 50 ? "bg-derived" : "bg-conflicting";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full rounded-full", tone)} style={{ width: `${pct}%` }} />
      </div>
      <span className="data-value text-xs text-muted-foreground">{pct}%</span>
    </div>
  );
}
