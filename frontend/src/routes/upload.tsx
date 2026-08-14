import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useRef, useState } from "react";
import { FileUp, Plus } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/PageHeader";
import { PipelineStatusPanel } from "@/components/upload/PipelineStatusPanel";
import { useCreateProduct, useProducts, useUploadDocument } from "@/lib/veritas/hooks";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "Upload a document — VERITAS" },
      {
        name: "description",
        content:
          "Send a spec sheet, datasheet or certificate into the VERITAS verification pipeline and watch every stage run.",
      },
      { property: "og:title", content: "Upload a document — VERITAS" },
      {
        property: "og:description",
        content: "Ingest product documents and watch extraction, red-teaming and classification run live.",
      },
    ],
  }),
  component: UploadPage,
});

const ACCEPTED = ["application/pdf", "image/png", "image/jpeg"];
const MAX_BYTES = 20 * 1024 * 1024;

function guessDocType(filename: string) {
  const lower = filename.toLowerCase();
  if (lower.includes("spec")) return "pdf_spec";
  if (lower.includes("catalog")) return "catalog";
  if (lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image";
  return "pdf_spec";
}

function UploadPage() {
  const { data: products = [] } = useProducts();
  const createProduct = useCreateProduct();
  const upload = useUploadDocument();

  const [productId, setProductId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState("pdf_spec");
  const [dragging, setDragging] = useState(false);
  const [creating, setCreating] = useState(false);
  const [sku, setSku] = useState("");
  const [name, setName] = useState("");
  const [documentId, setDocumentId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const canUpload = useMemo(() => Boolean(productId) && Boolean(file), [productId, file]);

  function acceptFile(next: File | undefined) {
    if (!next) return;
    if (!ACCEPTED.includes(next.type)) {
      toast.error("Unsupported file", { description: "VERITAS reads PDF, PNG and JPG documents." });
      return;
    }
    if (next.size > MAX_BYTES) {
      toast.error("Upload failed", {
        description: "The file exceeded 20MB. Try a smaller file or split the document.",
      });
      return;
    }
    setFile(next);
    setDocType(guessDocType(next.name));
  }

  async function handleSubmit() {
    if (!canUpload || !file) return;
    try {
      const result = await upload.mutateAsync({ productId, file, docType });
      setDocumentId(result.document_id);
      toast.success("Uploaded", { description: `${file.name} entered the pipeline.` });
    } catch (error) {
      toast.error("Upload failed", { description: (error as Error).message });
    }
  }

  async function handleCreateProduct() {
    if (!sku.trim() || !name.trim()) return;
    const product = await createProduct.mutateAsync({ sku: sku.trim(), name: name.trim() });
    setProductId(product.id);
    setCreating(false);
    setSku("");
    setName("");
    toast.success("Product created", { description: `${product.sku} is ready for documents.` });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <PageHeader
        eyebrow="Ingestion"
        title="Upload a document"
        description="Pick the product the document belongs to, then drop the file. The pipeline starts immediately and reports every stage as it runs."
      />

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <label htmlFor="product" className="text-sm font-medium">
            Product
          </label>
          <button
            type="button"
            onClick={() => setCreating((v) => !v)}
            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
          >
            <Plus className="h-3 w-3" aria-hidden /> New product
          </button>
        </div>
        <select
          id="product"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          className="select-field w-full px-3.5 py-2.5 text-sm"
        >
          <option value="">Select a product…</option>
          {products.map((product) => (
            <option key={product.id} value={product.id}>
              {product.sku} — {product.name}
            </option>
          ))}
        </select>

        {creating ? (
          <div className="flex flex-wrap gap-2 rounded-sm border bg-surface p-3">
            <input
              value={sku}
              onChange={(e) => setSku(e.target.value)}
              placeholder="SKU"
              className="data-value w-full rounded-sm border sm:w-32 px-2 py-1.5 text-sm"
            />
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Product name"
              className="w-full flex-1 rounded-sm border px-2 py-1.5 text-sm"
            />
            <button
              type="button"
              onClick={handleCreateProduct}
              className="rounded-sm bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
            >
              Create
            </button>
          </div>
        ) : null}
      </section>

      <section>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            if (productId) setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            if (productId) acceptFile(e.dataTransfer.files[0]);
          }}
          className={cn(
            "rounded-md border border-dashed bg-surface px-4 py-10 sm:px-6 sm:py-12 text-center transition-colors",
            dragging && "border-primary bg-accent",
            !productId && "opacity-70",
          )}
        >
          <FileUp className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden />
          {productId ? (
            <>
              <p className="mt-3 text-sm">
                Drop a PDF, PNG or JPG here, or{" "}
                <button type="button" onClick={() => inputRef.current?.click()} className="text-primary underline">
                  browse your files
                </button>
                .
              </p>
              <p className="mt-1 text-xs text-muted-foreground">Maximum 20MB per document.</p>
            </>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">
              Select a product first — every document has to be attached to one.
            </p>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            className="sr-only"
            onChange={(e) => acceptFile(e.target.files?.[0])}
          />
        </div>

        {file ? (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-sm border bg-surface px-4 py-3">
            <div>
              <p className="data-value text-sm">{file.name}</p>
              <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(0)} KB</p>
            </div>
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              Document type
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="data-value select-field px-2.5 py-1.5 text-xs"
              >
                {["pdf_spec", "image", "catalog", "web"].map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              disabled={!canUpload || upload.isPending}
              onClick={handleSubmit}
              className="w-full rounded-sm bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50 sm:w-auto sm:py-2"
            >
              {upload.isPending ? "Uploading…" : "Run pipeline"}
            </button>
          </div>
        ) : null}
      </section>

      {documentId ? (
        <section className="space-y-3">
          <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Pipeline status</h2>
          <PipelineStatusPanel documentId={documentId} />
        </section>
      ) : null}
    </div>
  );
}
