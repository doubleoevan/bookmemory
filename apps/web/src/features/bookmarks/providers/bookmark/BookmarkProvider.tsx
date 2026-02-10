import { ReactNode, useCallback, useMemo, useReducer } from "react";

import type { BookmarkResponse } from "@bookmemory/contracts";
import { BookmarkContext } from "@/features/bookmarks/providers/bookmark/BookmarkContext";

export type BookmarkState = {
  bookmark?: BookmarkResponse;
};
type BookmarkAction = { type: "SET_BOOKMARK"; bookmark: BookmarkResponse };

const initialState: BookmarkState = {};

function bookmarkReducer(state: BookmarkState, action: BookmarkAction): BookmarkState {
  switch (action.type) {
    case "SET_BOOKMARK": {
      return { ...state, bookmark: action.bookmark };
    }

    default:
      return state;
  }
}

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(bookmarkReducer, initialState);

  const setBookmark = useCallback((bookmark: BookmarkResponse) => {
    dispatch({ type: "SET_BOOKMARK", bookmark });
  }, []);

  // memoize context to avoid rerendering consumers
  const value = useMemo(
    () => ({
      setBookmark,
      ...state,
    }),
    [state, setBookmark],
  );
  return <BookmarkContext.Provider value={value}>{children}</BookmarkContext.Provider>;
}
