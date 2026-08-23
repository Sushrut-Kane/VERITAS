import { createFileRoute } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { FileUp, Download, CheckCircle, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/PageHeader";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/batch-upload")({
  head: () => ({
    meta: [
      { title: "Batch upload — VERITAS" },
      {
        name: "description",
        content: "Upload a catalog CSV, enrich every row into the 252-column Delivery Format, and download the result.",
      },
      { property: "og:title", content: "Batch upload — VERITAS" },
      {
        property: "og:description",
        content: "Batch CSV enrichment to Delivery Format.",
      },
    ],
  }),
  component: BatchUploadPage,
});

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

type UploadState = "idle" | "uploading" | "done" | "error";

function BatchUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [state, setState] = useState<UploadState>("idle");
  const [rowCount, setRowCount] = useState<number | null>(null);
  const [resultBlob, setResultBlob] = useState<Blob | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function acceptFile(next: File | undefined) {
    if (!next) return;
    if (!next.name.toLowerCase().endsWith(".csv")) {
      toast.error("Unsupported file", { description: "Please upload a CSV file." });
      return;
    }
    setFile(next);
    setState("idle");
    setRowCount(null);
    setResultBlob(null);
    setErrorMessage("");
  }

  async function handleEnrich() {
    if (!file) return;
    setState("uploading");
    setErrorMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/delivery/enrich`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const blob = await res.blob();
      const text = await blob.text();

      // Count rows (excluding header)
      const lines = text.split("\n").filter((l) => l.trim().length > 0);
      const count = Math.max(0, lines.length - 1); // subtract header

      setResultBlob(blob);
      setRowCount(count);
      setState("done");
      toast.success("Enrichment complete", {
        description: `${count} row${count !== 1 ? "s" : ""} enriched into Delivery Format.`,
      });
    } catch (error) {
      setState("error");
      const msg = (error as Error).message;
      setErrorMessage(msg);
      toast.error("Enrichment failed", { description: msg });
    }
  }

  function handleDownload() {
    if (!resultBlob) return;
    const url = URL.createObjectURL(resultBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "delivery.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <PageHeader
        eyebrow="Batch enrichment"
        title="Batch upload"
        description="Upload a catalog CSV with Mfg_Part_Num, Part_Desc, Part_Manuf and brand columns. Every row is enriched into the 252-column Delivery Format and returned as a downloadable CSV."
      />

      <section>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            acceptFile(e.dataTransfer.files[0]);
          }}
          className={cn(
            "rounded-md border border-dashed bg-surface px-4 py-10 sm:px-6 sm:py-12 text-center transition-colors",
            dragging && "border-primary bg-accent",
          )}
        >
          <FileUp className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden />
          <p className="mt-3 text-sm">
            Drop a CSV here, or{" "}
            <button type="button" onClick={() => inputRef.current?.click()} className="text-primary underline">
              browse your files
            </button>
            .
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Accepts .csv files with columns: Mfg_Part_Num, Part_Desc, Part_Manuf, E1_Brand, Unilog_Brand, DIB_Brand.
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="sr-only"
            onChange={(e) => acceptFile(e.target.files?.[0])}
          />
        </div>

        {file ? (
          <div className="mt-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-sm border bg-surface px-4 py-3">
              <div>
                <p className="data-value text-sm">{file.name}</p>
                <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(0)} KB</p>
              </div>
              <button
                type="button"
                disabled={state === "uploading"}
                onClick={handleEnrich}
                className="w-full rounded-sm bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50 sm:w-auto sm:py-2"
              >
                {state === "uploading" ? "Enriching…" : "Enrich to Delivery Format"}
              </button>
            </div>

            {state === "uploading" && (
              <div className="flex items-center gap-3 rounded-sm border border-primary/20 bg-accent/50 px-4 py-3">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                <span className="text-sm text-muted-foreground">Processing rows…</span>
              </div>
            )}

            {state === "done" && rowCount !== null && (
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-green-500/30 bg-green-500/5 px-4 py-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" aria-hidden />
                  <span className="text-sm font-medium">
                    {rowCount} row{rowCount !== 1 ? "s" : ""} enriched
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleDownload}
                  className="inline-flex items-center gap-2 rounded-sm border border-primary bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  <Download className="h-3.5 w-3.5" aria-hidden />
                  Download Delivery CSV
                </button>
              </div>
            )}

            {state === "error" && (
              <div className="flex items-center gap-2 rounded-sm border border-red-500/30 bg-red-500/5 px-4 py-3">
                <AlertCircle className="h-4 w-4 text-red-500" aria-hidden />
                <span className="text-sm text-red-600">{errorMessage || "Something went wrong."}</span>
              </div>
            )}
          </div>
        ) : null}
      </section>
    </div>
  );
}
