import { formatEvent, formatTimestamp } from "@/lib/veritas/format";
import type { AuditEntry } from "@/lib/veritas/schemas";

export function AuditTrail({ entries }: { entries: AuditEntry[] }) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Chain of custody</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Every event that touched this value, in order, with timestamps.
        </p>
      </div>
      <ol className="relative space-y-6 border-l pl-6">
        {entries.map((entry, i) => (
          <li key={`${entry.created_at}-${i}`} className="relative">
            <span
              className="absolute -left-[1.68rem] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-background bg-primary"
              aria-hidden
            />
            <p className="data-value text-[11px] uppercase tracking-[0.14em] text-muted-foreground">
              {formatTimestamp(entry.created_at)}
            </p>
            <p className="mt-1 text-sm font-medium capitalize">{formatEvent(entry.event_type)}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
