import { ReactNode, useCallback, useMemo, useReducer } from "react";

import { SummaryContext } from "@/features/bookmarks/providers/summary/SummaryContext";

export type SummaryState = {
  isLoading: boolean;
  summary: string;
};
type SummaryAction =
  | { type: "SET_IS_LOADING"; isLoading: boolean }
  | { type: "SET_SUMMARY"; summary: string };

const initialState: SummaryState = {
  isLoading: false,
  summary: "",
};

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
    // clear the current summary before regenerating
    dispatch({ type: "SET_SUMMARY", summary: "" });
    dispatch({ type: "SET_IS_LOADING", isLoading: true });
    try {
      console.log(`TODO: start summary for bookmark ${bookmarkId}`);
    } finally {
      dispatch({ type: "SET_IS_LOADING", isLoading: false });
    }
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
