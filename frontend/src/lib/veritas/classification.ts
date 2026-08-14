import type { Classification, PolicyDecision } from "./schemas";

type Meta = { label: string; description: string; className: string };

export const CLASSIFICATION_META: Record<Classification, Meta> = {
  verified: {
    label: "Verified",
    description: "Independent sources state the same value in the same terms.",
    className: "border-verified/30 bg-verified-soft text-verified",
  },
  derived: {
    label: "Derived",
    description: "Sources agree only after the pipeline normalized units or formats.",
    className: "border-derived/30 bg-derived-soft text-derived",
  },
  inferred: {
    label: "Inferred",
    description: "Value was reasoned from related evidence, not stated outright.",
    className: "border-derived/30 bg-derived-soft text-derived",
  },
  conflicting: {
    label: "Conflicting",
    description: "Sources disagree — a human has to rule before anything publishes.",
    className: "border-conflicting/30 bg-conflicting-soft text-conflicting",
  },
  unsupported: {
    label: "Unsupported",
    description: "No source carries enough weight to back the claim.",
    className: "border-unsupported/30 bg-unsupported-soft text-unsupported",
  },
};

export const POLICY_META: Record<PolicyDecision, Meta> = {
  publish: {
    label: "Published",
    description: "Cleared policy and reached the catalog.",
    className: "border-verified/30 bg-verified-soft text-verified",
  },
  human_review: {
    label: "Human review",
    description: "Held back for a reviewer decision.",
    className: "border-derived/30 bg-derived-soft text-derived",
  },
  blocked: {
    label: "Blocked",
    description: "Refused publication by the policy engine.",
    className: "border-unsupported/30 bg-unsupported-soft text-unsupported",
  },
};

export const CLASSIFICATIONS = Object.keys(CLASSIFICATION_META) as Classification[];

export function classificationMeta(value: Classification) {
  return CLASSIFICATION_META[value];
}

export function policyMeta(value: PolicyDecision) {
  return POLICY_META[value];
}
