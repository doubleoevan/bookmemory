import { ReactNode, useCallback, useMemo, useReducer } from "react";

import { SummaryContext } from "@/features/bookmarks/providers/summary/SummaryContext";
import { streamSummary } from "@/api";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";

export type SummaryState = {
  isLoading: boolean;
  summary: string;
};
type SummaryAction =
  | { type: "SET_IS_LOADING"; isLoading: boolean }
  | { type: "SET_SUMMARY"; summary: string }
  | { type: "APPEND_SUMMARY_CHUNK"; chunk: string };

const initialState: SummaryState = {
  isLoading: false,
  summary: "",
};

function summaryReducer(state: SummaryState, action: SummaryAction): SummaryState {
  switch (action.type) {
    case "SET_IS_LOADING": {
      return { ...state, isLoading: action.isLoading };
    }

    case "SET_SUMMARY": {
      return { ...state, summary: action.summary };
    }

    case "APPEND_SUMMARY_CHUNK": {
      const { chunk } = action;
      return { ...state, summary: state.summary + chunk };
    }

    default:
      return state;
  }
}

export function SummaryProvider({ children }: { children: ReactNode }) {
  const { refreshBookmark } = useBookmarks();
  const [state, dispatch] = useReducer(summaryReducer, initialState);

  const setSummary = useCallback((summary: string) => {
    // set the initial bookmark summary
    dispatch({ type: "SET_SUMMARY", summary });
  }, []);

  const startSummary = useCallback(
    async (bookmarkId: string) => {
      // clear the current summary before regenerating
      dispatch({ type: "SET_SUMMARY", summary: "" });
      dispatch({ type: "SET_IS_LOADING", isLoading: true });
      void streamSummary({
        bookmarkId,
        onChunk: (chunk) => {
          dispatch({ type: "APPEND_SUMMARY_CHUNK", chunk });
        },
        onComplete: () => {
          // update the bookmark in the context state with the new summary
          void refreshBookmark(bookmarkId);
          dispatch({ type: "SET_IS_LOADING", isLoading: false });
        },
        onError: () => {
          dispatch({ type: "SET_IS_LOADING", isLoading: false });
        },
      });
    },
    [refreshBookmark],
  );

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
