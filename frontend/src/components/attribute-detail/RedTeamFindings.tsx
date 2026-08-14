import { Check, ShieldAlert, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";
import type { RedTeamFinding } from "@/lib/veritas/schemas";

const CHECK_LABEL: Record<string, string> = {
  unit_consistency: "Unit consistency",
  contradiction: "Contradiction",
  evidence_sufficiency: "Evidence sufficiency",
};

const RESULT_LABEL: Record<string, string> = {
  pass: "Pass",
  fail: "Fail",
  pass_after_normalization: "Pass after normalization",
};

export function RedTeamFindings({ findings }: { findings: RedTeamFinding[] }) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Red-team findings</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Adversarial checks run against the model's own output before anything is allowed to publish.
        </p>
      </div>
      <ul className="overflow-hidden rounded-md border bg-surface">
        {findings.map((finding) => {
          const failed = finding.result === "fail";
          const normalized = finding.result === "pass_after_normalization";
          const Icon = failed ? ShieldAlert : normalized ? Wrench : Check;
          return (
            <li key={finding.check} className="flex gap-3 border-b px-5 py-4 last:border-b-0">
              <span
                className={cn(
                  "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-sm border",
                  failed && "border-conflicting/30 bg-conflicting-soft text-conflicting",
                  normalized && "border-derived/30 bg-derived-soft text-derived",
                  !failed && !normalized && "border-verified/30 bg-verified-soft text-verified",
                )}
              >
                <Icon className="h-3.5 w-3.5" aria-hidden />
              </span>
              <div>
                <p className="text-sm font-medium">
                  {CHECK_LABEL[finding.check] ?? finding.check}
                  <span
                    className={cn(
                      "ml-2 text-xs font-normal",
                      failed ? "text-conflicting" : normalized ? "text-derived" : "text-verified",
                    )}
                  >
                    {RESULT_LABEL[finding.result] ?? finding.result}
                  </span>
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{finding.detail}</p>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
