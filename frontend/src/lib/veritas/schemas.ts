/**
 * Zod schemas & TypeScript types — aligned with INTEGRATION.md contract.
 *
 * Every type here maps 1:1 to a backend response shape so contract drift
 * is caught at parse time, not in a React component three clicks deep.
 */
import { z } from "zod";

// ── Enums ──────────────────────────────────────────────────────────

export const classificationSchema = z.enum([
  "verified",
  "derived",
  "inferred",
  "conflicting",
  "unsupported",
]);
export type Classification = z.infer<typeof classificationSchema>;

export const policyDecisionSchema = z.enum(["publish", "human_review", "blocked"]);
export type PolicyDecision = z.infer<typeof policyDecisionSchema>;

// ── §3.1 Product ───────────────────────────────────────────────────

export const productSchema = z.object({
  id: z.string(),
  sku: z.string(),
  name: z.string().nullable(),
  created_at: z.string(),
});
export type Product = z.infer<typeof productSchema>;

// ── §3.2 Document upload ───────────────────────────────────────────

export const documentUploadResponseSchema = z.object({
  document_id: z.string(),
  status: z.string(),
});
export type DocumentUploadResponse = z.infer<typeof documentUploadResponseSchema>;

// ── §3.3 Pipeline status ──────────────────────────────────────────

export const pipelineStatusSchema = z.object({
  document_id: z.string(),
  status: z.string(), // "extracting" | "cross_checking" | ... | "done" | "error"
  attributes_processed: z.number(),
  attributes_total: z.number(),
  error: z.string().nullable(),
});
export type PipelineStatus = z.infer<typeof pipelineStatusSchema>;

// ── §3.4 Attribute summary (used in product attributes + review queue) ──

export const attributeSummarySchema = z.object({
  id: z.string(),
  attr_key: z.string(),
  attr_value: z.string(),
  classification: classificationSchema.nullable(),
  classification_confidence: z.number().nullable(),
  policy_decision: policyDecisionSchema.nullable(),
  source_count: z.number(),
});
export type AttributeSummary = z.infer<typeof attributeSummarySchema>;

export const productAttributesResponseSchema = z.object({
  product_id: z.string(),
  attributes: z.array(attributeSummarySchema),
});
export type ProductAttributesResponse = z.infer<typeof productAttributesResponseSchema>;

// ── §3.5 Attribute detail ─────────────────────────────────────────

export const sourceDocumentSchema = z.object({
  id: z.string(),
  filename: z.string(),
  doc_type: z.string(),
});

export const claimSchema = z.object({
  claim_id: z.string(),
  raw_value: z.string(),
  normalized_value: z.string(),
  source_document: sourceDocumentSchema,
  source_span: z.string(),
  extraction_confidence: z.number(),
});
export type Claim = z.infer<typeof claimSchema>;

export const redTeamFindingSchema = z.object({
  check: z.string(),
  result: z.string(),
  detail: z.string(),
});
export type RedTeamFinding = z.infer<typeof redTeamFindingSchema>;

export const auditEntrySchema = z.object({
  event_type: z.string(),
  created_at: z.string(),
});
export type AuditEntry = z.infer<typeof auditEntrySchema>;

export const attributeDetailSchema = z.object({
  id: z.string(),
  attr_key: z.string(),
  attr_value: z.string(),
  classification: classificationSchema.nullable(),
  classification_confidence: z.number().nullable(),
  reasoning: z.string().nullable(),
  policy_decision: policyDecisionSchema.nullable(),
  claims: z.array(claimSchema),
  red_team_findings: z.array(redTeamFindingSchema),
  audit_log: z.array(auditEntrySchema),
});
export type AttributeDetail = z.infer<typeof attributeDetailSchema>;

// ── §3.6 Attribute graph ──────────────────────────────────────────

export const graphNodeSchema = z.object({
  id: z.string(),
  type: z.string(),
  label: z.string(),
});

export const graphEdgeSchema = z.object({
  from: z.string(),
  to: z.string(),
  type: z.string(),
});

export const attributeGraphSchema = z.object({
  nodes: z.array(graphNodeSchema),
  edges: z.array(graphEdgeSchema),
});
export type AttributeGraph = z.infer<typeof attributeGraphSchema>;

// ── §3.8 Review action ────────────────────────────────────────────

export const reviewActionSchema = z.object({
  action: z.enum(["approve", "reject", "edit"]),
  edited_value: z.string().optional(),
  reviewer_note: z.string().optional(),
});
export type ReviewAction = z.infer<typeof reviewActionSchema>;

// ── §3.9 Catalog ──────────────────────────────────────────────────

export const catalogAttributeSchema = z.object({
  attr_key: z.string(),
  attr_value: z.string(),
  trust_badge: z.string(),
});

export const catalogProductSchema = z.object({
  sku: z.string(),
  name: z.string().nullable(),
  attributes: z.array(catalogAttributeSchema),
});

export const catalogResponseSchema = z.object({
  products: z.array(catalogProductSchema),
});
export type CatalogResponse = z.infer<typeof catalogResponseSchema>;
export type CatalogProduct = z.infer<typeof catalogProductSchema>;
export type CatalogAttribute = z.infer<typeof catalogAttributeSchema>;
