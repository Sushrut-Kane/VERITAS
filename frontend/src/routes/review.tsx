import { createFileRoute, Link } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/PageHeader";
import { ConfidenceBar, StatusBadge } from "@/components/veritas/ClassificationBadge";
import { CLASSIFICATION_META, CLASSIFICATIONS } from "@/lib/veritas/classification";
import { useReviewQueue } from "@/lib/veritas/hooks";
import { useUiStore } from "@/lib/store/uiStore";
import type { Classification } from "@/lib/veritas/schemas";

export const Route = createFileRoute("/review")({
  head: () => ({
    meta: [
      { title: "Review queue — VERITAS" },
      {
        name: "description",
        content: "Triage every attribute the policy engine held back: conflicting, derived and low-confidence values.",
      },
      { property: "og:title", content: "Review queue — VERITAS" },
      {
        property: "og:description",
        content: "Everything the policy engine refused to auto-publish, lowest confidence first.",
      },
    ],
  }),
  component: ReviewPage,
});

function ReviewPage() {
  const { data, isPending } = useReviewQueue();
  const { reviewClassification, reviewProduct, setReviewClassification, setReviewProduct } = useUiStore();

  const rows = (data ?? []).filter(
    (row) =>
      (reviewClassification === "all" || row.classification === reviewClassification) &&
      reviewProduct === "all", // product filter simplified — review-queue no longer carries sku
  );

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <PageHeader
        eyebrow="Triage"
        title="Review queue"
        description="Attributes the policy engine wouldn't publish on its own. Lowest confidence first — open a row to see the evidence behind it."
      />

      <div className="grid grid-cols-1 gap-3 sm:flex sm:flex-wrap">
        <select
          value={reviewClassification}
          onChange={(e) => setReviewClassification(e.target.value as never)}
          className="select-field px-3.5 py-2.5 text-sm sm:py-2"
          aria-label="Filter by classification"
        >
          <option value="all">All classifications</option>
          {CLASSIFICATIONS.map((c) => (
            <option key={c} value={c}>
              {CLASSIFICATION_META[c].label}
            </option>
          ))}
        </select>
      </div>

      {isPending ? (
        <div className="space-y-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-14 animate-pulse rounded-sm bg-muted" />
          ))}
        </div>
      ) : rows.length === 0 ? (
        <div className="rounded-md border bg-surface px-6 py-16 text-center">
          <p className="text-sm font-medium">Nothing needs review right now.</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Every attribute cleared policy on its own.{" "}
            <Link to="/catalog" className="text-primary underline">
              See what published
            </Link>
            .
          </p>
        </div>
      ) : (
        <>
          <ul className="space-y-3 md:hidden">
            {rows.map((row) => (
              <li key={row.id} className="rounded-md border bg-surface">
                <Link to="/attribute/$id" params={{ id: row.id }} className="block px-4 py-4">
                  <p className="data-value mt-2 text-sm font-medium">{row.attr_key}</p>
                  <p className="data-value mt-1 text-sm text-muted-foreground">{row.attr_value}</p>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <StatusBadge classification={row.classification as Classification} />
                    <ConfidenceBar value={row.classification_confidence ?? 0} />
                  </div>
                  <p className="mt-3 text-xs text-muted-foreground">
                    {CLASSIFICATION_META[row.classification as Classification]?.description}
                  </p>
                </Link>
              </li>
            ))}
          </ul>

          <div className="hidden overflow-x-auto rounded-md border bg-surface md:block">
            <table className="w-full min-w-[56rem] text-sm">

            <thead className="bg-muted/60 text-left text-xs uppercase tracking-[0.14em] text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Attribute</th>
                <th className="px-4 py-3 font-medium">Value</th>
                <th className="px-4 py-3 font-medium">Classification</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Sources</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {rows.map((row) => (
                <tr key={row.id} className="transition-colors hover:bg-accent/40">
                  <td className="data-value px-4 py-3">
                    <Link to="/attribute/$id" params={{ id: row.id }} className="block">
                      {row.attr_key}
                    </Link>
                  </td>
                  <td className="data-value px-4 py-3">{row.attr_value}</td>
                  <td className="px-4 py-3">
                    <StatusBadge classification={row.classification as Classification} />
                  </td>
                  <td className="px-4 py-3">
                    <ConfidenceBar value={row.classification_confidence ?? 0} />
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {row.source_count} source{row.source_count !== 1 ? "s" : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </>
      )}


    </div>
  );
}
