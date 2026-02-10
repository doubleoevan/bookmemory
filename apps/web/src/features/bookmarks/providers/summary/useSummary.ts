import { useContext } from "react";
import { type SummaryContextValue } from "@/features/bookmarks/providers/summary/index";
import { SummaryContext } from "@/features/bookmarks/providers/summary/SummaryContext";

export function useSummary(): SummaryContextValue {
  const context = useContext(SummaryContext);
  if (!context) {
    throw new Error("useSummary must be used within <SummaryProvider />");
  }
  return context;
}
