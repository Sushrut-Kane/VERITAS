import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  CheckCircle2,
  Database,
  FileCheck2,
  Layers,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Upload,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatusBadge, ConfidenceBar } from "@/components/veritas/ClassificationBadge";
import { useCatalog, useProducts, useReviewQueue, useLovCompliance } from "@/lib/veritas/hooks";
import { useUiStore } from "@/lib/store/uiStore";
import type { Classification } from "@/lib/veritas/schemas";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — VERITAS" },
      {
        name: "description",
        content: "Overview of verified product attributes, red-team findings, policy decisions, and LOV compliance.",
      },
      { property: "og:title", content: "Dashboard — VERITAS" },
      {
        property: "og:description",
        content: "Product intelligence overview, verification stats, and triage metrics.",
      },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  const demoUser = useUiStore((s) => s.demoUser);
  const { data: products = [], isPending: productsLoading } = useProducts();
  const { data: catalogData, isPending: catalogLoading } = useCatalog();
  const { data: reviewQueue = [], isPending: reviewLoading } = useReviewQueue();
  const { data: lovData, isPending: lovLoading } = useLovCompliance();

  const publishedProducts = catalogData?.products ?? [];
  const publishedAttributeCount = publishedProducts.reduce(
    (acc, p) => acc + (p.attributes?.length ?? 0),
    0,
  );

  // Group review queue items by classification
  const classificationCounts: Record<Classification, number> = {
    verified: 0,
    derived: 0,
    inferred: 0,
    conflicting: 0,
    unsupported: 0,
  };

  // Tally published items by trust badge
  publishedProducts.forEach((product) => {
    product.attributes.forEach((attr) => {
      const badge = attr.trust_badge as Classification;
      if (badge in classificationCounts) {
        classificationCounts[badge] = (classificationCounts[badge] || 0) + 1;
      }
    });
  });

  // Tally review queue items by classification
  reviewQueue.forEach((item) => {
    const key = item.classification as Classification;
    if (key in classificationCounts) {
      classificationCounts[key] = (classificationCounts[key] || 0) + 1;
    }
  });

  const totalAttributesCount = publishedAttributeCount + reviewQueue.length;
  const reviewCount = reviewQueue.length;

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <PageHeader
        eyebrow="Intelligence Overview"
        title={demoUser ? `Welcome back, ${demoUser.split("@")[0]}` : "Firewall Dashboard"}
        description="Real-time visibility into ingested catalog products, adversarial verification, policy triage, and reference taxonomy compliance."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 rounded-sm bg-primary px-3.5 py-2 text-xs font-medium text-primary-foreground shadow-sm hover:opacity-90"
            >
              <Upload className="h-3.5 w-3.5" aria-hidden /> Upload document
            </Link>
            <Link
              to="/review"
              className="inline-flex items-center gap-1.5 rounded-sm border bg-surface px-3.5 py-2 text-xs font-medium hover:bg-accent"
            >
              <ShieldAlert className="h-3.5 w-3.5 text-orange-500" aria-hidden /> Review queue ({reviewCount})
            </Link>
          </div>
        }
      />

      {/* KPI Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Products */}
        <div className="rounded-md border bg-surface p-5 transition-shadow hover:shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] uppercase tracking-[0.16em] font-medium">Catalog Products</span>
            <Layers className="h-4 w-4 text-primary" aria-hidden />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-value text-3xl font-semibold tracking-tight">
              {productsLoading ? "—" : products.length}
            </span>
            <span className="text-xs text-muted-foreground">registered SKUs</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {publishedProducts.length} published with clean attributes
          </p>
        </div>

        {/* Published Attributes */}
        <div className="rounded-md border bg-surface p-5 transition-shadow hover:shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] uppercase tracking-[0.16em] font-medium">Published Attributes</span>
            <FileCheck2 className="h-4 w-4 text-green-500" aria-hidden />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-value text-3xl font-semibold tracking-tight text-foreground">
              {catalogLoading ? "—" : publishedAttributeCount}
            </span>
            <span className="text-xs text-muted-foreground">active specs</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Passed adversarial red-teaming & policy gate
          </p>
        </div>

        {/* Needs Review */}
        <div className={cn(
          "rounded-md border bg-surface p-5 transition-shadow hover:shadow-sm",
          reviewCount > 0 && "border-orange-500/40 bg-orange-500/5"
        )}>
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] uppercase tracking-[0.16em] font-medium">Action Required</span>
            <AlertTriangle className={cn("h-4 w-4", reviewCount > 0 ? "text-orange-500" : "text-muted-foreground")} aria-hidden />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className={cn(
              "data-value text-3xl font-semibold tracking-tight",
              reviewCount > 0 ? "text-orange-600" : "text-foreground"
            )}>
              {reviewLoading ? "—" : reviewCount}
            </span>
            <span className="text-xs text-muted-foreground">held in review queue</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {reviewCount > 0 ? (
              <Link to="/review" className="text-orange-600 underline font-medium inline-flex items-center gap-1">
                Triage pending items <ArrowRight className="h-3 w-3" />
              </Link>
            ) : (
              "All attributes cleared verification"
            )}
          </p>
        </div>

        {/* LOV Taxonomy Compliance */}
        <div className="rounded-md border bg-surface p-5 transition-shadow hover:shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] uppercase tracking-[0.16em] font-medium">LOV Compliance</span>
            <CheckCircle2 className="h-4 w-4 text-primary" aria-hidden />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-value text-3xl font-semibold tracking-tight">
              {lovLoading
                ? "—"
                : lovData?.compliance_pct !== null && lovData?.compliance_pct !== undefined
                ? `${lovData.compliance_pct.toFixed(0)}%`
                : "N/A"}
            </span>
            <span className="text-xs text-muted-foreground">reference match</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {lovData?.matched ?? 0} of {lovData?.total_attributes ?? 0} attributes in standard taxonomy
          </p>
        </div>
      </section>

      {/* Main Breakdown Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Classification Breakdown (2 cols) */}
        <section className="rounded-md border bg-surface p-6 lg:col-span-2 space-y-5">
          <div className="flex items-center justify-between border-b pb-4">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em]">
                Classification & Trust Distribution
              </h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Distribution of verified claims across the 5-tier industrial data taxonomy.
              </p>
            </div>
            <span className="data-value text-xs text-muted-foreground">
              {totalAttributesCount} total attributes evaluated
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {/* Verified */}
            <div className="rounded-sm border border-green-500/20 bg-green-500/5 p-3.5">
              <div className="flex items-center justify-between">
                <StatusBadge classification="verified" />
                <span className="data-value text-lg font-semibold text-green-600">
                  {classificationCounts.verified}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Direct evidence match with corroborated source spans. Automatically cleared for publication.
              </p>
            </div>

            {/* Derived */}
            <div className="rounded-sm border border-yellow-500/20 bg-yellow-500/5 p-3.5">
              <div className="flex items-center justify-between">
                <StatusBadge classification="derived" />
                <span className="data-value text-lg font-semibold text-yellow-600">
                  {classificationCounts.derived}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Normalized equivalent (e.g. °F $\leftrightarrow$ °C or fractional dimensions) requiring inspection.
              </p>
            </div>

            {/* Inferred */}
            <div className="rounded-sm border border-yellow-500/20 bg-yellow-500/5 p-3.5">
              <div className="flex items-center justify-between">
                <StatusBadge classification="inferred" />
                <span className="data-value text-lg font-semibold text-yellow-600">
                  {classificationCounts.inferred}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Contextual derivation strongly implied by product description text.
              </p>
            </div>

            {/* Conflicting */}
            <div className="rounded-sm border border-orange-500/20 bg-orange-500/5 p-3.5">
              <div className="flex items-center justify-between">
                <StatusBadge classification="conflicting" />
                <span className="data-value text-lg font-semibold text-orange-600">
                  {classificationCounts.conflicting}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Flagged by Red-Teaming: cross-document discrepancy or OEM/brand mismatch.
              </p>
            </div>

            {/* Unsupported */}
            <div className="rounded-sm border border-red-500/20 bg-red-500/5 p-3.5 sm:col-span-2">
              <div className="flex items-center justify-between">
                <StatusBadge classification="unsupported" />
                <span className="data-value text-lg font-semibold text-red-600">
                  {classificationCounts.unsupported}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Blocked by policy: ungrounded claim lacking verified document span evidence.
              </p>
            </div>
          </div>
        </section>

        {/* System & Engine Architecture Status (1 col) */}
        <section className="rounded-md border bg-surface p-6 space-y-4">
          <div className="border-b pb-3">
            <h2 className="text-sm font-semibold uppercase tracking-[0.14em]">
              Firewall Infrastructure
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Connected data services and AI pipelines.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-start justify-between rounded-sm border bg-muted/40 p-3">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-primary" aria-hidden />
                <div>
                  <p className="font-medium text-foreground">Supabase PostgreSQL</p>
                  <p className="text-muted-foreground text-[11px]">pgvector & reference LOV tables</p>
                </div>
              </div>
              <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-0.5 text-[10px] font-medium text-green-600 border border-green-500/30">
                Connected
              </span>
            </div>

            <div className="flex items-start justify-between rounded-sm border bg-muted/40 p-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-green-600" aria-hidden />
                <div>
                  <p className="font-medium text-foreground">Red-Team Firewall</p>
                  <p className="text-muted-foreground text-[11px]">Contradiction & Unit Normalization</p>
                </div>
              </div>
              <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-0.5 text-[10px] font-medium text-green-600 border border-green-500/30">
                Active
              </span>
            </div>

            <div className="flex items-start justify-between rounded-sm border bg-muted/40 p-3">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" aria-hidden />
                <div>
                  <p className="font-medium text-foreground">AI Intelligence Model</p>
                  <p className="text-muted-foreground text-[11px]">Claude 3.5 Sonnet / Deterministic</p>
                </div>
              </div>
              <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary border border-primary/30">
                Ready
              </span>
            </div>
          </div>

          <div className="border-t pt-3">
            <Link
              to="/catalog"
              className="inline-flex w-full items-center justify-center gap-1.5 rounded-sm border bg-surface px-3 py-2 text-xs font-medium transition-colors hover:bg-accent text-foreground"
            >
              Browse complete catalog <ExternalLink className="h-3.5 w-3.5" />
            </Link>
          </div>
        </section>
      </div>

      {/* Review Queue Preview */}
      <section className="rounded-md border bg-surface overflow-hidden">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.14em]">
              Recent Review Queue Items
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Attributes held back by policy engine, awaiting human triage decision.
            </p>
          </div>
          {reviewCount > 0 ? (
            <Link to="/review" className="text-xs text-primary font-medium underline inline-flex items-center gap-1">
              View all ({reviewCount}) <ArrowRight className="h-3 w-3" />
            </Link>
          ) : null}
        </header>

        {reviewLoading ? (
          <div className="p-6 space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-10 animate-pulse rounded bg-muted" />
            ))}
          </div>
        ) : reviewQueue.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle2 className="mx-auto h-8 w-8 text-green-500" aria-hidden />
            <p className="mt-3 text-sm font-medium">Review queue is empty</p>
            <p className="mt-1 text-xs text-muted-foreground">
              All extracted product attributes cleared verification checks.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-left text-xs uppercase tracking-[0.14em] text-muted-foreground border-b">
                <tr>
                  <th className="px-5 py-3 font-medium">Attribute Key</th>
                  <th className="px-5 py-3 font-medium">Value</th>
                  <th className="px-5 py-3 font-medium">Classification</th>
                  <th className="px-5 py-3 font-medium">Confidence</th>
                  <th className="px-5 py-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {reviewQueue.slice(0, 5).map((item) => (
                  <tr key={item.id} className="transition-colors hover:bg-accent/40">
                    <td className="data-value px-5 py-3.5 font-medium">{item.attr_key}</td>
                    <td className="data-value px-5 py-3.5 text-muted-foreground">{item.attr_value}</td>
                    <td className="px-5 py-3.5">
                      <StatusBadge classification={item.classification as Classification} />
                    </td>
                    <td className="px-5 py-3.5">
                      <ConfidenceBar value={item.classification_confidence ?? 0} />
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        to="/attribute/$id"
                        params={{ id: item.id }}
                        className="inline-flex items-center gap-1 rounded-sm border px-2.5 py-1 text-xs font-medium transition-colors hover:bg-accent text-primary"
                      >
                        Inspect <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
