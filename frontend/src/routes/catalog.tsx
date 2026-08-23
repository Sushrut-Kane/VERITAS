import { createFileRoute, Link } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/PageHeader";
import { useCatalog, useLovCompliance } from "@/lib/veritas/hooks";
import { useUiStore } from "@/lib/store/uiStore";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/catalog")({
  head: () => ({
    meta: [
      { title: "Published catalog — VERITAS" },
      {
        name: "description",
        content: "Every product attribute that cleared verification, red-teaming and policy — the clean end state.",
      },
      { property: "og:title", content: "Published catalog — VERITAS" },
      { property: "og:description", content: "Verified product attributes that passed every check." },
    ],
  }),
  component: CatalogPage,
});

/** §5 trust badge color mapping */
function TrustBadge({ badge }: { badge: string }) {
  const colors: Record<string, string> = {
    verified: "bg-green-500/10 text-green-500 border-green-500/30",
    derived: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
    inferred: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
    conflicting: "bg-orange-500/10 text-orange-500 border-orange-500/30",
    unsupported: "bg-red-500/10 text-red-500 border-red-500/30",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider",
        colors[badge] ?? colors.verified,
      )}
    >
      {badge}
    </span>
  );
}

/** LOV compliance stat tile */
function LovComplianceTile() {
  const { data, isPending } = useLovCompliance();

  if (isPending) {
    return (
      <div className="h-24 animate-pulse rounded-md bg-muted" />
    );
  }

  const hasData = data?.compliance_pct !== null && data?.compliance_pct !== undefined;

  return (
    <div className="rounded-md border bg-surface px-5 py-4">
      <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
        LOV compliance
      </p>
      {hasData ? (
        <div className="mt-2 flex items-baseline gap-3">
          <span className="data-value text-2xl font-semibold tracking-tight">
            {data!.compliance_pct!.toFixed(1)}%
          </span>
          <span className="text-xs text-muted-foreground">
            {data!.matched} of {data!.total_attributes} attribute values in LOV
          </span>
        </div>
      ) : (
        <div className="mt-2">
          <span className="text-sm text-muted-foreground italic">
            Reference data not loaded
          </span>
          <p className="mt-1 text-xs text-muted-foreground/70">
            Run <code className="data-value text-[11px]">scripts/load_reference_data.py</code> to populate LOV tables.
          </p>
        </div>
      )}
    </div>
  );
}

function CatalogPage() {
  const { data, isPending } = useCatalog();
  const search = useUiStore((s) => s.catalogSearch);
  const setSearch = useUiStore((s) => s.setCatalogSearch);

  const term = search.trim().toLowerCase();
  const products = (data?.products ?? [])
    .map((entry) => ({
      ...entry,
      attributes: term
        ? entry.attributes.filter(
            (a) => a.attr_key.toLowerCase().includes(term) || entry.sku.toLowerCase().includes(term),
          )
        : entry.attributes,
    }))
    .filter((entry) => entry.attributes.length > 0);

  // §5 warn if unsupported attributes appear in catalog (treat as bug)
  products.forEach((entry) =>
    entry.attributes.forEach((a) => {
      if (a.trust_badge === "unsupported") {
        console.warn(`[VERITAS] Unsupported attribute reached the catalog: ${a.attr_key} — this is a bug`);
      }
    }),
  );

  return (
    <div className="mx-auto max-w-5xl space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <PageHeader
        eyebrow="Published"
        title="Catalog"
        description="What actually reaches commerce. Every row here survived cross-checking, adversarial review and the policy gate."
        actions={
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search SKU or attribute"
            className="w-full rounded-sm border sm:w-56 bg-surface px-3 py-2 text-sm"
            aria-label="Search catalog"
          />
        }
      />

      <LovComplianceTile />

      {isPending ? (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="h-32 animate-pulse rounded-md bg-muted" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="rounded-md border bg-surface px-6 py-16 text-center">
          <p className="text-sm font-medium">No published attributes yet.</p>
          <p className="mt-1 text-sm text-muted-foreground">
            <Link to="/upload" className="text-primary underline">
              Upload a document
            </Link>{" "}
            to get started.
          </p>
        </div>
      ) : (
        products.map((entry) => (
          <section key={entry.sku} className="overflow-hidden rounded-md border bg-surface">
            <header className="flex items-baseline gap-3 border-b px-5 py-3">
              <span className="data-value text-sm font-semibold">{entry.sku}</span>
              <span className="text-sm text-muted-foreground">{entry.name}</span>
            </header>
            <ul className="divide-y">
              {entry.attributes.map((attribute, idx) => (
                <li key={`${attribute.attr_key}-${idx}`}>
                  <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3">
                    <span className="data-value text-sm">{attribute.attr_key}</span>
                    <span className="flex items-center gap-4">
                      <span className="data-value text-sm text-muted-foreground">{attribute.attr_value}</span>
                      <TrustBadge badge={attribute.trust_badge} />
                      {attribute.trust_badge === "conflicting" && (
                        <Link to="/review" className="text-xs text-orange-500 underline">
                          Review
                        </Link>
                      )}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))
      )}
    </div>
  );
}

