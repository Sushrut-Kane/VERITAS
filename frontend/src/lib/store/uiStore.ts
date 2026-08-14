import { create } from "zustand";
import type { Classification } from "@/lib/veritas/schemas";

type UiState = {
  reviewClassification: Classification | "all";
  reviewProduct: string | "all";
  catalogSearch: string;
  demoUser: string | null;
  setReviewClassification: (value: Classification | "all") => void;
  setReviewProduct: (value: string | "all") => void;
  setCatalogSearch: (value: string) => void;
  signIn: (email: string) => void;
  signOut: () => void;
};

export const useUiStore = create<UiState>((set) => ({
  reviewClassification: "all",
  reviewProduct: "all",
  catalogSearch: "",
  demoUser: null,
  setReviewClassification: (reviewClassification) => set({ reviewClassification }),
  setReviewProduct: (reviewProduct) => set({ reviewProduct }),
  setCatalogSearch: (catalogSearch) => set({ catalogSearch }),
  signIn: (demoUser) => set({ demoUser }),
  signOut: () => set({ demoUser: null }),
}));
