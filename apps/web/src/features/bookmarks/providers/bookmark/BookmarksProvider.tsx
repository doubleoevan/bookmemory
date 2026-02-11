import { ReactNode, useCallback, useMemo, useReducer, useRef } from "react";

import type { BookmarkResponse, LimitOffsetPageBookmarkResponse } from "@bookmemory/contracts";
import { getBookmarks, GetBookmarksQuery } from "@/api";
import { BookmarksContext } from "@/features/bookmarks/providers/bookmark/BookmarksContext";

export type BookmarkState = {
  bookmark?: BookmarkResponse;
  bookmarks: BookmarkResponse[];
  isLoading: boolean;
  total: number;
  limit: number;
  offset: number;
};
type BookmarkAction =
  | { type: "SET_IS_LOADING"; isLoading: boolean }
  | {
      type: "ADD_BOOKMARKS_PAGE";
      bookmarksPage: LimitOffsetPageBookmarkResponse;
    }
  | { type: "SET_BOOKMARK"; bookmark: BookmarkResponse };

const initialState: BookmarkState = {
  bookmarks: [],
  isLoading: false,
  total: 0,
  limit: 10,
  offset: 0,
};

function toPageQuery(query: GetBookmarksQuery = {}): string {
  return JSON.stringify({
    ...query,
    tag: query.tag ? [...query.tag].sort() : query.tag,
  });
}

function bookmarkReducer(state: BookmarkState, action: BookmarkAction): BookmarkState {
  switch (action.type) {
    case "SET_IS_LOADING": {
      return { ...state, isLoading: action.isLoading };
    }

    case "ADD_BOOKMARKS_PAGE": {
      // add a new page to the list of bookmarks
      const { items, total, limit, offset } = action.bookmarksPage;
      const bookmarks = [...state.bookmarks, ...items];
      return {
        ...state,
        bookmarks,
        total,
        limit,
        offset: offset + items.length,
      };
    }

    case "SET_BOOKMARK": {
      return { ...state, bookmark: action.bookmark };
    }

    default:
      return state;
  }
}

export function BookmarksProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(bookmarkReducer, initialState);
  const pageQueriesRef = useRef<Set<string>>(new Set());

  const getBookmarksPage = useCallback(
    async (params?: {
      search?: string | null;
      tag?: string[];
      tag_mode?: "any" | "all" | "ignore";
      sort?: "alphabetical" | "recent";
      limit?: number;
    }) => {
      // set the limit and offset for pagination
      const query = {
        search: params?.search,
        tag: params?.tag,
        tag_mode: params?.tag_mode,
        sort: params?.sort,
        limit: params?.limit || state.limit,
        offset: state.offset,
      } satisfies GetBookmarksQuery;

      // prevent duplicate page requests
      const pageQuery = toPageQuery(query);
      if (pageQueriesRef.current.has(pageQuery)) {
        return;
      }
      pageQueriesRef.current.add(pageQuery);

      // add the bookmarks page
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmarksPage = await getBookmarks(query);
        dispatch({ type: "ADD_BOOKMARKS_PAGE", bookmarksPage });
      } finally {
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
        pageQueriesRef.current.delete(pageQuery);
      }
    },
    [state.limit, state.offset],
  );

  const setBookmark = useCallback((bookmark: BookmarkResponse) => {
    dispatch({ type: "SET_BOOKMARK", bookmark });
  }, []);

  // memoize context to avoid rerendering consumers
  const value = useMemo(
    () => ({
      getBookmarksPage,
      setBookmark,
      ...state,
    }),
    [getBookmarksPage, setBookmark, state],
  );
  return <BookmarksContext.Provider value={value}>{children}</BookmarksContext.Provider>;
}
