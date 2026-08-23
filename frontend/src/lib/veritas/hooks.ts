/**
 * React Query hooks — thin wrappers around the API layer.
 *
 * These are the only interface between React components and the backend.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addProduct,
  fetchAttribute,
  fetchCatalog,
  fetchLovCompliance,
  fetchPipelineStatus,
  fetchReviewQueue,
  listProducts,
  submitReview,
  uploadDocument,
} from "./api";
import type { ReviewAction } from "./schemas";

export const useProducts = () => useQuery({ queryKey: ["products"], queryFn: listProducts });

export function useCreateProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sku, name }: { sku: string; name: string }) => addProduct(sku, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products"] }),
  });
}

export const useUploadDocument = () =>
  useMutation({
    mutationFn: ({ productId, file, docType }: { productId: string; file: File; docType: string }) =>
      uploadDocument(productId, file, docType),
  });

export function usePipelineStatus(documentId: string | null) {
  return useQuery({
    queryKey: ["pipeline-status", documentId],
    queryFn: () => fetchPipelineStatus(documentId!),
    enabled: Boolean(documentId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "done" || status === "error" ? false : 1500;
    },
  });
}

export const useAttributeDetail = (id: string) =>
  useQuery({ queryKey: ["attribute", id], queryFn: () => fetchAttribute(id) });

export const useReviewQueue = () =>
  useQuery({ queryKey: ["review-queue"], queryFn: fetchReviewQueue, staleTime: 5_000 });

export const useCatalog = () => useQuery({ queryKey: ["catalog"], queryFn: fetchCatalog });

export function useReviewAction(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (action: ReviewAction) => submitReview(id, action),
    onSuccess: () =>
      Promise.all([
        qc.invalidateQueries({ queryKey: ["attribute", id] }),
        qc.invalidateQueries({ queryKey: ["review-queue"] }),
        qc.invalidateQueries({ queryKey: ["catalog"] }),
      ]),
  });
}

export const useLovCompliance = () =>
  useQuery({ queryKey: ["lov-compliance"], queryFn: fetchLovCompliance, staleTime: 30_000 });

