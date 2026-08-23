/**
 * API boundary — calls the real FastAPI backend.
 *
 * Every function validates its payload with zod before handing data to hooks,
 * so contract drift fails loudly instead of leaking undefined.
 *
 * When VITE_API_BASE_URL is not set, falls back to the in-memory mock backend
 * so the UI can still demo without infrastructure.
 */
import { z } from "zod";
import {
  attributeDetailSchema,
  attributeSummarySchema,
  catalogResponseSchema,
  documentUploadResponseSchema,
  pipelineStatusSchema,
  productSchema,
  type ReviewAction,
} from "./schemas";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = !API_BASE;

// ── Error handling ───────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(schema: z.ZodType<T>, path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...getAuthHeader(),
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let errorBody: { error?: { code?: string; message?: string } } = {};
    try {
      errorBody = await res.json();
    } catch {
      // response isn't JSON
    }
    throw new ApiError(
      errorBody.error?.code ?? "unknown",
      errorBody.error?.message ?? `Request failed (${res.status})`,
      res.status,
    );
  }

  const data = await res.json();
  return schema.parse(data);
}

// ── Auth token management ────────────────────────────────────────

let _token: string | null = null;

export function setAuthToken(token: string) {
  _token = token;
}

export function getAuthToken(): string | null {
  return _token;
}

function getAuthHeader(): Record<string, string> {
  return _token ? { Authorization: `Bearer ${_token}` } : {};
}

// ── Mock fallback (lazy-loaded only when needed) ─────────────────

let mockModule: typeof import("./mock-backend") | null = null;

async function getMock() {
  if (!mockModule) {
    mockModule = await import("./mock-backend");
  }
  return mockModule;
}

function mockResolve<T>(schema: z.ZodType<T>, data: unknown, delay = 240): Promise<T> {
  return new Promise((r) => setTimeout(() => r(schema.parse(data)), delay));
}

// ── API functions ────────────────────────────────────────────────

export async function listProducts() {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(z.array(productSchema), m.products);
  }
  return request(z.array(productSchema), "/products");
}

export async function addProduct(sku: string, name: string) {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(productSchema, m.createProduct(sku, name));
  }
  return request(productSchema, "/products", {
    method: "POST",
    body: JSON.stringify({ sku, name }),
  });
}

export async function uploadDocument(productId: string, file: File, docType: string) {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(
      documentUploadResponseSchema,
      { document_id: m.startRun(productId, file.name), status: "queued" },
      600,
    );
  }
  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_type", docType);
  return request(documentUploadResponseSchema, `/products/${productId}/documents`, {
    method: "POST",
    body: formData,
  });
}

export async function fetchPipelineStatus(documentId: string) {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(pipelineStatusSchema, m.getPipelineStatus(documentId), 120);
  }
  return request(pipelineStatusSchema, `/pipeline-status/${documentId}`);
}

export async function fetchAttribute(id: string) {
  if (USE_MOCK) {
    const m = await getMock();
    const found = m.attributes.find((a) => a.id === id);
    if (!found) throw new ApiError("not_found", "That attribute no longer exists.", 404);
    return mockResolve(attributeDetailSchema, found);
  }
  return request(attributeDetailSchema, `/attributes/${id}`);
}

export async function fetchReviewQueue() {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(
      z.array(attributeSummarySchema),
      m.attributes
        .filter((a) => a.policy_decision === "human_review")
        .map(m.toSummary)
        .sort((a, b) => (a.classification_confidence ?? 0) - (b.classification_confidence ?? 0)),
    );
  }
  return request(z.array(attributeSummarySchema), "/review-queue");
}

export async function fetchCatalog() {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(
      catalogResponseSchema,
      {
        products: m.products
          .map((product) => ({
            ...product,
            attributes: m.attributes
              .filter((a) => a.product_id === product.id && a.policy_decision === "publish")
              .map((a) => ({
                attr_key: a.attr_key ?? a.key,
                attr_value: a.attr_value ?? a.value,
                trust_badge: a.classification ?? "verified",
              })),
          }))
          .filter((entry) => entry.attributes.length > 0),
      },
    );
  }
  return request(catalogResponseSchema, "/catalog");
}

export async function submitReview(id: string, action: ReviewAction) {
  if (USE_MOCK) {
    const m = await getMock();
    return mockResolve(attributeDetailSchema, m.applyReview(id, action), 400);
  }
  return request(attributeDetailSchema, `/attributes/${id}/review`, {
    method: "POST",
    body: JSON.stringify(action),
  });
}

// ── LOV Compliance ───────────────────────────────────────────────

const lovComplianceSchema = z.object({
  compliance_pct: z.number().nullable(),
  total_attributes: z.number(),
  matched: z.number(),
  message: z.string(),
});

export type LovCompliance = z.infer<typeof lovComplianceSchema>;

export async function fetchLovCompliance(): Promise<LovCompliance> {
  if (USE_MOCK) {
    return {
      compliance_pct: null,
      total_attributes: 0,
      matched: 0,
      message: "Reference data not loaded",
    };
  }
  return request(lovComplianceSchema, "/delivery/lov-compliance");
}

