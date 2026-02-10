import { createContext } from "react";
import { SummaryState } from "@/features/bookmarks/providers/summary/SummaryProvider";

export type SummaryContextValue = SummaryState & {
  setSummary: (summary: string) => void;
  startSummary: (bookmarkId: string) => void;
  stopSummary: () => void;
};

export const SummaryContext = createContext<SummaryContextValue | null>(null);
