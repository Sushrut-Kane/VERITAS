import { ArrowRight, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatConfidence } from "@/lib/veritas/format";
import type { Claim } from "@/lib/veritas/schemas";

export function EvidencePanel({ claims }: { claims: Claim[] }) {
  return (
    <section className="space-y-4">
      <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Evidence</h2>
      <div className={cn("grid gap-4", claims.length === 2 && "md:grid-cols-2")}>
        {claims.map((claim) => {
          const converted = claim.raw_value !== claim.normalized_value;
          return (
            <article key={claim.claim_id} className="rounded-md border bg-surface p-5">
              <header className="flex items-center gap-2 border-b pb-3">
                <FileText className="h-4 w-4 text-muted-foreground" aria-hidden />
                <span className="data-value text-sm">{claim.source_document.filename}</span>
                <span className="ml-auto rounded-sm bg-muted px-2 py-0.5 text-[10px] uppercase tracking-[0.1em] text-muted-foreground">
                  {claim.source_document.doc_type}
                </span>
              </header>

              <div className="mt-4 flex flex-wrap items-center gap-3">
                <span className="data-value rounded-sm border px-2.5 py-1.5 text-sm">{claim.raw_value}</span>
                {converted ? (
                  <>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" aria-hidden />
                    <span className="data-value rounded-sm border border-verified/40 bg-verified-soft px-2.5 py-1.5 text-sm text-verified">
                      {claim.normalized_value}
                    </span>
                    <span className="text-xs text-muted-foreground">normalized by the pipeline</span>
                  </>
                ) : (
                  <span className="text-xs text-muted-foreground">no conversion needed</span>
                )}
              </div>

              <blockquote className="mt-4 border-l-2 border-primary/40 pl-3 text-sm text-muted-foreground">
                “{claim.source_span}”
              </blockquote>

              <p className="mt-4 text-xs text-muted-foreground">
                Extraction confidence <span className="data-value">{formatConfidence(claim.extraction_confidence)}</span>
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
