import {
  PIPELINE_STAGES,
  type AttributeDetail,
  type PipelineStatus,
  type Product,
  type ReviewAction,
} from "./schemas";

/**
 * In-memory demo backend. Mirrors the INTEGRATION.md response shapes so the UI
 * can be swapped onto the real API by changing lib/veritas/api.ts only.
 */

const now = Date.now();
const iso = (offsetMs: number) => new Date(now + offsetMs).toISOString();

export const products: Product[] = [
  { id: "prd_1", sku: "AC-7741", name: "Aurora Convection Oven" },
  { id: "prd_2", sku: "TH-2210", name: "Thermion Kettle 1.7L" },
  { id: "prd_3", sku: "NV-0093", name: "Novara Induction Hob" },
];

export const attributes: AttributeDetail[] = [
  {
    id: "att_1",
    product_id: "prd_1",
    product_sku: "AC-7741",
    product_name: "Aurora Convection Oven",
    key: "max_operating_temperature",
    value: "80 °C",
    classification: "derived",
    policy_decision: "human_review",
    confidence: 0.71,
    reasoning:
      "Two sources state the same limit in different units. The spec sheet reports 176°F, the datasheet 80°C. After normalization both agree, so the value is Derived rather than Verified — the agreement depends on a unit conversion the pipeline performed, not on two independent identical statements.",
    claims: [
      {
        id: "clm_1",
        source_document: "aurora-spec-sheet.pdf",
        doc_type: "spec_sheet",
        raw_value: "176°F",
        normalized_value: "80 °C",
        source_span: "Maximum sustained cavity temperature: 176°F under continuous load.",
        extraction_confidence: 0.93,
      },
      {
        id: "clm_2",
        source_document: "aurora-datasheet.pdf",
        doc_type: "datasheet",
        raw_value: "80 °C",
        normalized_value: "80 °C",
        source_span: "Operating range 20 °C – 80 °C (ambient 25 °C).",
        extraction_confidence: 0.88,
      },
    ],
    red_team: [
      {
        check: "unit_consistency",
        status: "pass_after_normalization",
        detail: "176°F converted to 80.0°C; matches the datasheet value within 0.1°C tolerance.",
      },
      {
        check: "contradiction",
        status: "pass",
        detail: "No source states a conflicting maximum temperature.",
      },
      {
        check: "evidence_sufficiency",
        status: "pass",
        detail: "Two independent documents support the claim.",
      },
    ],
    audit_log: [
      { timestamp: iso(-620000), event: "extracted", description: "Claim parsed from aurora-spec-sheet.pdf" },
      { timestamp: iso(-600000), event: "extracted", description: "Claim parsed from aurora-datasheet.pdf" },
      { timestamp: iso(-580000), event: "normalized", description: "176°F converted to 80 °C" },
      { timestamp: iso(-560000), event: "red_team", description: "Unit consistency check passed after normalization" },
      { timestamp: iso(-540000), event: "classified", description: "Classified Derived (confidence 0.71)" },
      { timestamp: iso(-520000), event: "policy", description: "Routed to human review — below publish threshold 0.80" },
    ],
  },
  {
    id: "att_2",
    product_id: "prd_1",
    product_sku: "AC-7741",
    product_name: "Aurora Convection Oven",
    key: "power_rating",
    value: "2400 W",
    classification: "verified",
    policy_decision: "published",
    confidence: 0.96,
    reasoning:
      "Both the datasheet and the compliance certificate state 2400 W verbatim, in the same unit, with no conflicting statement anywhere in the document set.",
    claims: [
      {
        id: "clm_3",
        source_document: "aurora-datasheet.pdf",
        doc_type: "datasheet",
        raw_value: "2400 W",
        normalized_value: "2400 W",
        source_span: "Rated power input: 2400 W @ 230 V / 50 Hz.",
        extraction_confidence: 0.97,
      },
      {
        id: "clm_4",
        source_document: "ce-certificate.pdf",
        doc_type: "certificate",
        raw_value: "2400 W",
        normalized_value: "2400 W",
        source_span: "Declared rating 2400 W, tested per EN 60335-2-6.",
        extraction_confidence: 0.95,
      },
    ],
    red_team: [
      { check: "unit_consistency", status: "pass", detail: "Both claims already expressed in watts." },
      { check: "contradiction", status: "pass", detail: "No contradicting power figure found." },
      { check: "evidence_sufficiency", status: "pass", detail: "Two independent sources, one of them a certificate." },
    ],
    audit_log: [
      { timestamp: iso(-900000), event: "extracted", description: "Claim parsed from aurora-datasheet.pdf" },
      { timestamp: iso(-880000), event: "extracted", description: "Claim parsed from ce-certificate.pdf" },
      { timestamp: iso(-860000), event: "red_team", description: "All three adversarial checks passed" },
      { timestamp: iso(-840000), event: "classified", description: "Classified Verified (confidence 0.96)" },
      { timestamp: iso(-820000), event: "published", description: "Auto-published to catalog" },
    ],
  },
  {
    id: "att_3",
    product_id: "prd_2",
    product_sku: "TH-2210",
    product_name: "Thermion Kettle 1.7L",
    key: "capacity",
    value: "1.7 L",
    classification: "verified",
    policy_decision: "published",
    confidence: 0.94,
    reasoning:
      "Capacity is stated identically on the packaging artwork and the datasheet, and matches the product title.",
    claims: [
      {
        id: "clm_5",
        source_document: "thermion-datasheet.pdf",
        doc_type: "datasheet",
        raw_value: "1.7 L",
        normalized_value: "1.7 L",
        source_span: "Usable capacity 1.7 L (max fill line).",
        extraction_confidence: 0.96,
      },
    ],
    red_team: [
      { check: "unit_consistency", status: "pass", detail: "Single unit system (litres) throughout." },
      { check: "contradiction", status: "pass", detail: "Packaging artwork agrees with the datasheet." },
      { check: "evidence_sufficiency", status: "pass", detail: "Supported by a primary source plus product title." },
    ],
    audit_log: [
      { timestamp: iso(-1500000), event: "extracted", description: "Claim parsed from thermion-datasheet.pdf" },
      { timestamp: iso(-1480000), event: "classified", description: "Classified Verified (confidence 0.94)" },
      { timestamp: iso(-1460000), event: "published", description: "Auto-published to catalog" },
    ],
  },
  {
    id: "att_4",
    product_id: "prd_2",
    product_sku: "TH-2210",
    product_name: "Thermion Kettle 1.7L",
    key: "warranty_period",
    value: "3 years",
    classification: "conflicting",
    policy_decision: "human_review",
    confidence: 0.42,
    reasoning:
      "The marketing brochure claims a 3-year warranty while the warranty card states 2 years. The two statements cannot both be true; the pipeline refuses to publish either without a human ruling.",
    claims: [
      {
        id: "clm_6",
        source_document: "thermion-brochure.pdf",
        doc_type: "marketing",
        raw_value: "3 years",
        normalized_value: "36 months",
        source_span: "Backed by our industry-leading 3-year warranty.",
        extraction_confidence: 0.81,
      },
      {
        id: "clm_7",
        source_document: "warranty-card.png",
        doc_type: "warranty",
        raw_value: "24 months",
        normalized_value: "24 months",
        source_span: "This appliance is warranted for 24 months from date of purchase.",
        extraction_confidence: 0.89,
      },
    ],
    red_team: [
      { check: "unit_consistency", status: "pass_after_normalization", detail: "3 years normalized to 36 months for comparison." },
      { check: "contradiction", status: "fail", detail: "36 months vs 24 months — direct conflict between marketing and warranty card." },
      { check: "evidence_sufficiency", status: "pass", detail: "Both claims are well-sourced; the problem is disagreement, not sparsity." },
    ],
    audit_log: [
      { timestamp: iso(-400000), event: "extracted", description: "Claim parsed from thermion-brochure.pdf" },
      { timestamp: iso(-390000), event: "extracted", description: "Claim parsed from warranty-card.png" },
      { timestamp: iso(-380000), event: "red_team", description: "Contradiction check failed" },
      { timestamp: iso(-370000), event: "classified", description: "Classified Conflicting (confidence 0.42)" },
      { timestamp: iso(-360000), event: "policy", description: "Blocked from publish — routed to human review" },
    ],
  },
  {
    id: "att_5",
    product_id: "prd_3",
    product_sku: "NV-0093",
    product_name: "Novara Induction Hob",
    key: "energy_class",
    value: "A++",
    classification: "unsupported",
    policy_decision: "blocked",
    confidence: 0.18,
    reasoning:
      "The only mention of an energy class appears in a promotional headline with no test reference and no certificate in the document set. Nothing supports the claim, so it is not published.",
    claims: [
      {
        id: "clm_8",
        source_document: "novara-launch-flyer.pdf",
        doc_type: "marketing",
        raw_value: "A++",
        normalized_value: "A++",
        source_span: "The most efficient hob in its class — A++ performance.",
        extraction_confidence: 0.44,
      },
    ],
    red_team: [
      { check: "unit_consistency", status: "pass", detail: "No unit conversion required." },
      { check: "contradiction", status: "pass", detail: "No competing statement found." },
      { check: "evidence_sufficiency", status: "fail", detail: "Single marketing source, no certificate or test report." },
    ],
    audit_log: [
      { timestamp: iso(-300000), event: "extracted", description: "Claim parsed from novara-launch-flyer.pdf" },
      { timestamp: iso(-290000), event: "red_team", description: "Evidence sufficiency check failed" },
      { timestamp: iso(-280000), event: "classified", description: "Classified Unsupported (confidence 0.18)" },
      { timestamp: iso(-270000), event: "policy", description: "Blocked — insufficient evidence to publish" },
    ],
  },
  {
    id: "att_6",
    product_id: "prd_3",
    product_sku: "NV-0093",
    product_name: "Novara Induction Hob",
    key: "zone_count",
    value: "4",
    classification: "verified",
    policy_decision: "published",
    confidence: 0.98,
    reasoning: "Zone count is stated in the datasheet and visible in the labelled installation diagram.",
    claims: [
      {
        id: "clm_9",
        source_document: "novara-datasheet.pdf",
        doc_type: "datasheet",
        raw_value: "4",
        normalized_value: "4",
        source_span: "Four independent induction zones (2 × 180 mm, 2 × 145 mm).",
        extraction_confidence: 0.98,
      },
    ],
    red_team: [
      { check: "unit_consistency", status: "pass", detail: "Dimensionless count." },
      { check: "contradiction", status: "pass", detail: "Installation diagram agrees." },
      { check: "evidence_sufficiency", status: "pass", detail: "Primary source plus diagram." },
    ],
    audit_log: [
      { timestamp: iso(-1200000), event: "extracted", description: "Claim parsed from novara-datasheet.pdf" },
      { timestamp: iso(-1180000), event: "classified", description: "Classified Verified (confidence 0.98)" },
      { timestamp: iso(-1160000), event: "published", description: "Auto-published to catalog" },
    ],
  },
];

type Run = { documentId: string; productId: string; filename: string; startedAt: number };
const runs = new Map<string, Run>();

export function createProduct(sku: string, name: string): Product {
  const product = { id: `prd_${products.length + 1}_${Date.now()}`, sku, name };
  products.push(product);
  return product;
}

export function startRun(productId: string, filename: string): string {
  const documentId = `doc_${Math.random().toString(36).slice(2, 9)}`;
  runs.set(documentId, { documentId, productId, filename, startedAt: Date.now() });
  return documentId;
}

const STAGE_MS = 2200;

export function getPipelineStatus(documentId: string): PipelineStatus {
  const run = runs.get(documentId);
  if (!run) {
    return {
      document_id: documentId,
      filename: "unknown",
      status: "error",
      stage: "extracting",
      attributes_processed: 0,
      attributes_total: 0,
      message: "That document isn't in this session. Upload it again to start a new run.",
      attributes: [],
    };
  }
  const elapsed = Date.now() - run.startedAt;
  const index = Math.min(Math.floor(elapsed / STAGE_MS), PIPELINE_STAGES.length - 1);
  const stage = PIPELINE_STAGES[index]!;
  const done = stage === "done";
  const produced = attributes.filter((a) => a.product_id === run.productId);
  const total = produced.length || 3;
  return {
    document_id: documentId,
    filename: run.filename,
    status: done ? "done" : "running",
    stage,
    attributes_processed: done ? total : Math.min(total, Math.round((index / (PIPELINE_STAGES.length - 1)) * total)),
    attributes_total: total,
    message: null,
    attributes: done ? produced.map(toSummary) : [],
  };
}

export function toSummary(a: AttributeDetail) {
  const { reasoning: _r, claims: _c, red_team: _rt, audit_log: _al, ...summary } = a;
  return summary;
}

export function applyReview(id: string, action: ReviewAction): AttributeDetail {
  const attribute = attributes.find((a) => a.id === id);
  if (!attribute) throw new Error("Attribute not found.");
  const stamp = new Date().toISOString();
  if (action.action === "edit" && action.value) {
    attribute.value = action.value;
    attribute.audit_log.push({
      timestamp: stamp,
      event: "human_edit",
      description: `Reviewer set the value to ${action.value}`,
    });
  }
  if (action.action === "reject") {
    attribute.policy_decision = "blocked";
    attribute.audit_log.push({ timestamp: stamp, event: "rejected", description: "Reviewer rejected the value" });
  } else {
    attribute.policy_decision = "published";
    attribute.classification = "verified";
    attribute.audit_log.push({
      timestamp: stamp,
      event: "published",
      description: "Reviewer approved — published to catalog",
    });
  }
  return attribute;
}
