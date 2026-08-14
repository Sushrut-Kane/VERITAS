import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronLeft } from "lucide-react";
import { AuditTrail } from "@/components/attribute-detail/AuditTrail";
import { EvidencePanel } from "@/components/attribute-detail/EvidencePanel";
import { RedTeamFindings } from "@/components/attribute-detail/RedTeamFindings";
import { ReviewActionBar } from "@/components/attribute-detail/ReviewActionBar";
import { ConfidenceBar, StatusBadge } from "@/components/veritas/ClassificationBadge";
import type { Classification, PolicyDecision } from "@/lib/veritas/schemas";

export const Route = createFileRoute("/attribute/$id")({
  head: () => ({
    meta: [
      { title: "Attribute evidence — VERITAS" },
      {
        name: "description",
        content:
          "The full reasoning trail behind one product attribute: source evidence, red-team findings and chain of custody.",
      },
      { property: "og:title", content: "Attribute evidence — VERITAS" },
      { property: "og:description", content: "See exactly why VERITAS classified and routed this value." },
    ],
  }),
  component: AttributePage,
});

import { useAttributeDetail } from "@/lib/veritas/hooks";

function AttributePage() {
  const { id } = Route.useParams();
  const { data, isPending, isError, error } = useAttributeDetail(id);

  if (isPending) {
    return (
      <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6 sm:py-10">
        <div className="h-24 animate-pulse rounded-md bg-muted" />
        <div className="h-40 animate-pulse rounded-md bg-muted" />
        <div className="h-64 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 text-center">
        <p className="text-sm font-medium">We couldn't load this attribute.</p>
        <p className="mt-1 text-sm text-muted-foreground">{(error as Error)?.message ?? "Try reloading the page."}</p>
        <Link to="/review" className="mt-4 inline-block text-sm text-primary underline">
          Back to the review queue
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-12 px-4 py-8 sm:px-6 sm:py-10">
      <div>
        <Link
          to={data.policy_decision === "human_review" ? "/review" : "/catalog"}
          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="h-3 w-3" aria-hidden />
          {data.policy_decision === "human_review" ? "Review queue" : "Catalog"}
        </Link>

        <header className="mt-4 border-b pb-6">
          <h1 className="data-value mt-3 break-words text-2xl font-semibold sm:text-3xl tracking-tight">{data.attr_key}</h1>
          <p className="data-value mt-2 break-words text-xl text-primary sm:text-2xl">{data.attr_value}</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <StatusBadge classification={data.classification as Classification} size="lg" />
            <StatusBadge policy={data.policy_decision as PolicyDecision} size="lg" />
            <ConfidenceBar value={data.classification_confidence ?? 0} />
          </div>
        </header>
      </div>

      <section>
        <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Reasoning</h2>
        <p className="mt-3 text-base leading-relaxed sm:text-lg">{data.reasoning}</p>
      </section>

      <EvidencePanel claims={data.claims} />
      <RedTeamFindings findings={data.red_team_findings} />
      <AuditTrail entries={data.audit_log} />

      {data.policy_decision === "human_review" ? <ReviewActionBar id={data.id} currentValue={data.attr_value} /> : null}
    </div>
  );
}
