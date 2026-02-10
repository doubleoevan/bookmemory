import { ReactNode, useCallback, useMemo, useReducer } from "react";

import { SummaryContext } from "@/features/bookmarks/providers/summary/SummaryContext";

export type SummaryState = { summary: string };
type SummaryAction = { type: "SET_SUMMARY"; summary: string };

const initialState: SummaryState = { summary: "" };

function summaryReducer(state: SummaryState, action: SummaryAction): SummaryState {
  switch (action.type) {
    case "SET_SUMMARY": {
      return { ...state, summary: action.summary };
    }

    default:
      return state;
  }
}

export function SummaryProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(summaryReducer, initialState);

  const setSummary = useCallback((summary: string) => {
    // set the initial bookmark summary
    dispatch({ type: "SET_SUMMARY", summary });
  }, []);

  const startSummary = useCallback((bookmarkId: string) => {
    // clear the bookmark summary before regenerating
    console.log(`TODO: start summary for bookmark ${bookmarkId}`);
    dispatch({ type: "SET_SUMMARY", summary: "" });
  }, []);

  const stopSummary = useCallback(() => {}, []);

  // memoize context to avoid rerendering consumers
  const value = useMemo(
    () => ({
      setSummary,
      startSummary,
      stopSummary,
      ...state,
    }),
    [state, setSummary, startSummary, stopSummary],
  );
  return <SummaryContext.Provider value={value}>{children}</SummaryContext.Provider>;
}
