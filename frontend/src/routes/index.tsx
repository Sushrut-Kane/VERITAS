import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, FileSearch, GitBranch, ShieldAlert } from "lucide-react";
import { StatusBadge } from "@/components/veritas/ClassificationBadge";
import { Reveal } from "@/components/veritas/Reveal";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "VERITAS — evidence-backed product attributes" },
      {
        name: "description",
        content:
          "VERITAS extracts product attributes from source documents, red-teams its own output, and publishes only what the evidence supports.",
      },
      { property: "og:title", content: "VERITAS — evidence-backed product attributes" },
      {
        property: "og:description",
        content: "Extraction, adversarial review and a full chain of custody for every published product attribute.",
      },
    ],
  }),
  component: Landing,
});

const pillars = [
  {
    icon: FileSearch,
    title: "Every value traced to a span",
    body: "Each attribute links back to the exact sentence in the exact document it came from, with the extraction confidence attached.",
  },
  {
    icon: ShieldAlert,
    title: "The model attacks its own output",
    body: "Unit consistency, contradiction and evidence sufficiency checks run adversarially before anything is allowed near the catalog.",
  },
  {
    icon: GitBranch,
    title: "A visible chain of custody",
    body: "Extraction, normalization, red-team verdict, classification, policy decision and human ruling — timestamped, in order.",
  },
];

function Landing() {
  return (
    <div>
      <section className="rule-grid border-b">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-24">
          <Reveal delay={0}>
            <p className="data-value text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
              Product attribute verification
            </p>
          </Reveal>
          <Reveal delay={80}>
            <h1 className="mt-6 max-w-3xl text-3xl font-semibold leading-tight sm:text-4xl md:text-5xl sm:leading-[1.05] tracking-tight">
              Publish the attributes your documents actually support.
            </h1>
          </Reveal>
          <Reveal delay={160}>
            <p className="mt-5 max-w-2xl text-base sm:text-lg text-muted-foreground">
              VERITAS reads spec sheets, datasheets and certificates, cross-checks every claim, attacks its own
              conclusions, and routes anything it can't defend to a human.
            </p>
          </Reveal>
          <Reveal delay={240}>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                to="/upload"
                preload="intent"
                viewTransition
                className="group inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:shadow-primary/25"
              >
                Upload a document{" "}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden />
              </Link>
              <Link
                to="/review"
                preload="intent"
                viewTransition
                className="inline-flex items-center rounded-full border px-5 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
              >
                Open the review queue
              </Link>
            </div>
          </Reveal>

          <Reveal delay={320}>
            <div className="mt-14 flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">The taxonomy, used identically everywhere:</span>
              <StatusBadge classification="verified" />
              <StatusBadge classification="derived" />
              <StatusBadge classification="inferred" />
              <StatusBadge classification="conflicting" />
              <StatusBadge classification="unsupported" />
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-6 px-4 py-14 sm:px-6 sm:py-20 md:grid-cols-3">
        {pillars.map((pillar, i) => (
          <Reveal key={pillar.title} delay={i * 120} from="up">
            <article className="h-full rounded-md border bg-surface p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-primary/5">
              <pillar.icon className="h-5 w-5 text-primary" aria-hidden />
              <h2 className="mt-4 text-base font-medium">{pillar.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{pillar.body}</p>
            </article>
          </Reveal>
        ))}
      </section>

      <section className="border-t">
        <Reveal from="scale">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-10 sm:px-6 sm:py-12">
            <div>
              <h2 className="text-lg font-medium">See the clean end state</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Only Verified attributes reach the catalog. Everything else is held, with a reason.
              </p>
            </div>
            <Link
              to="/catalog"
              preload="intent"
              viewTransition
              className="rounded-full border px-5 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
            >
              Browse the catalog
            </Link>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
