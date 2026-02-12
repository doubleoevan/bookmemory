import { ReactNode, useCallback, useMemo, useReducer, useRef } from "react";

import {
  BookmarkCreateRequest,
  BookmarkPreviewRequest,
  BookmarkPreviewResponse,
  BookmarkResponse,
  BookmarkSearchRequest,
  BookmarkSearchResponse,
  BookmarkUpdateRequest,
  LimitOffsetPageBookmarkResponse,
} from "@bookmemory/contracts";
import {
  createBookmark,
  deleteBookmark,
  getBookmarks,
  GetBookmarksQuery,
  getRelatedBookmarks,
  GetRelatedBookmarksQuery,
  loadBookmark,
  previewBookmark,
  searchBookmarks,
  updateBookmark,
} from "@/api";
import { BookmarksContext } from "@/features/bookmarks/providers/bookmark/BookmarksContext";

export type Sort = "alphabetical" | "recent";
export type BookmarkState = {
  bookmark?: BookmarkPreviewResponse;
  bookmarks: Array<BookmarkResponse | BookmarkPreviewResponse>;
  relatedBookmarks: BookmarkSearchResponse[];
  isLoading: boolean;
  userHasBookmarks: boolean;
  total: number; // total bookmarks for the current query
  limit: number;
  offset: number;
  sort: Sort;
};
type BookmarkAction =
  | { type: "SET_IS_LOADING"; isLoading: boolean }
  | { type: "SET_SORT"; sort: Sort }
  | {
      type: "ADD_BOOKMARKS_PAGE";
      bookmarksPage: LimitOffsetPageBookmarkResponse;
      setHasBookmarks?: boolean;
    }
  | { type: "ADD_SEARCH_BOOKMARKS"; bookmarks: BookmarkSearchResponse[] }
  | { type: "SET_RELATED_BOOKMARKS"; relatedBookmarks: BookmarkSearchResponse[] }
  | { type: "SET_BOOKMARK"; bookmark: BookmarkResponse };

const initialState: BookmarkState = {
  bookmarks: [],
  relatedBookmarks: [],
  isLoading: false,
  userHasBookmarks: false,
  total: 0,
  limit: 10,
  offset: 0,
  sort: "recent",
};

function toPageQuery(query: GetBookmarksQuery = {}): string {
  return JSON.stringify({
    ...query,
    tag: query.tag ? [...query.tag].sort() : query.tag,
  });
}

function isQueryFiltered(query: GetBookmarksQuery = {}): boolean {
  // check if the query has a search filter
  const search = query?.search?.trim() ?? "";
  const hasSearchFilter = search.length > 0;

  // check if the query has tags filter
  const tags = query?.tag ?? [];
  const tagMode = query?.tag_mode;
  const hasTagsFilter = tags.length > 0 && tagMode !== "ignore";

  // check if the query has an offset filter
  const offset = query?.offset;
  const hasOffsetFilter = offset !== undefined && offset > 0;
  return hasSearchFilter || hasTagsFilter || hasOffsetFilter;
}

function bookmarkReducer(state: BookmarkState, action: BookmarkAction): BookmarkState {
  switch (action.type) {
    case "SET_IS_LOADING": {
      return { ...state, isLoading: action.isLoading };
    }

    case "ADD_BOOKMARKS_PAGE": {
      // replace the first page or add a new page to the list of bookmarks
      const { items, total, limit, offset } = action.bookmarksPage;
      const bookmarks = offset === 0 ? items : [...state.bookmarks, ...items];
      return {
        ...state,
        bookmarks,
        userHasBookmarks: action.setHasBookmarks ? total > 0 : state.userHasBookmarks,
        total,
        limit,
        offset: offset + items.length,
      };
    }

    case "ADD_SEARCH_BOOKMARKS": {
      return { ...state, bookmarks: action.bookmarks };
    }

    case "SET_RELATED_BOOKMARKS": {
      return { ...state, relatedBookmarks: action.relatedBookmarks };
    }

    case "SET_BOOKMARK": {
      return { ...state, bookmark: action.bookmark };
    }

    case "SET_SORT": {
      return { ...state, sort: action.sort };
    }

    default:
      return state;
  }
}

export function BookmarksProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(bookmarkReducer, initialState);

  // put state in a ref to keep callbacks stable
  const stateRef = useRef(state);
  stateRef.current = state;

  // keep track of active page queries to prevent duplicate concurrent requests
  const pageQueriesRef = useRef<Set<string>>(new Set());

  const getBookmarksPage = useCallback(
    async (params?: {
      search?: string | null;
      tag?: string[];
      tag_mode?: "any" | "all" | "ignore";
      sort?: Sort;
      limit?: number;
      offset?: number;
    }) => {
      // set the limit and offset for pagination
      const query = {
        search: params?.search,
        tag: params?.tag,
        tag_mode: params?.tag_mode,
        sort: params?.sort ?? stateRef.current.sort,
        limit: params?.limit || stateRef.current.limit,
        offset: params?.offset ?? stateRef.current.offset,
      } satisfies GetBookmarksQuery;

      // prevent duplicate page requests
      const pageQuery = toPageQuery(query);
      if (pageQueriesRef.current.has(pageQuery)) {
        return;
      }
      pageQueriesRef.current.add(pageQuery);

      // update the has bookmarks flag if the query is not filtered
      const setHasBookmarks = !isQueryFiltered(query);

      // add the bookmarks page
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmarksPage = await getBookmarks(query);
        dispatch({ type: "ADD_BOOKMARKS_PAGE", bookmarksPage, setHasBookmarks });
      } finally {
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
        pageQueriesRef.current.delete(pageQuery);
      }
    },
    [],
  );

  const getBookmarksSearchPage = useCallback(
    async (params: {
      search: string;
      tag?: string[];
      tag_mode?: "any" | "all" | "ignore";
      limit?: number;
    }) => {
      // convert the params into a POST body
      const body = {
        search: params.search,
        tags: params.tag,
        tag_mode: params.tag_mode,
        limit: params.limit || stateRef.current.limit,
      } satisfies BookmarkSearchRequest;

      // add the bookmarks search page
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmarks = await searchBookmarks(body);
        dispatch({ type: "ADD_SEARCH_BOOKMARKS", bookmarks });
      } finally {
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
      }
    },
    [],
  );

  const addRelatedBookmarks = useCallback(
    async (params: { bookmarkId: string; tag_mode?: "any" | "all" | "ignore"; limit?: number }) => {
      // convert the params to a query object
      const query = {
        tag_mode: params.tag_mode,
        limit: params.limit,
      } satisfies GetRelatedBookmarksQuery;

      // set the related bookmarks
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const relatedBookmarks = await getRelatedBookmarks(params.bookmarkId, query);
        dispatch({ type: "SET_RELATED_BOOKMARKS", relatedBookmarks });
      } finally {
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
      }
    },
    [],
  );

  const addBookmark = useCallback(
    async (params: {
      title: string;
      description: string;
      url?: string | null;
      type?: "link" | "note" | "file";
      tags?: string[];
    }): Promise<BookmarkResponse> => {
      // convert the params into a POST body
      const body = {
        title: params.title,
        description: params.description,
        url: params.url,
        type: params.type,
        tags: params.tags,
      } satisfies BookmarkCreateRequest;

      // add the new bookmark
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmark = await createBookmark(body);
        loadBookmark(bookmark.id); // load the bookmark embeddings
        dispatch({ type: "SET_BOOKMARK", bookmark });
        return bookmark;
      } finally {
        // clear the loading flag and refresh the bookmarks list
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
        pageQueriesRef.current.clear();
        void getBookmarksPage({ offset: 0 });
      }
    },
    [getBookmarksPage],
  );

  const getBookmarkPreview = useCallback(
    async (params: { url: string; type?: "link" | "note" | "file" }): Promise<BookmarkResponse> => {
      // convert the params into a POST body
      const body = {
        url: params.url,
        type: params.type ?? "link",
      } satisfies BookmarkPreviewRequest;

      // add the new bookmark
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmark = await previewBookmark(body);
        dispatch({ type: "SET_BOOKMARK", bookmark });
        return bookmark;
      } finally {
        // clear the loading flag
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
      }
    },
    [],
  );

  const saveBookmark = useCallback(
    async (
      bookmarkId: string,
      params: {
        title?: string | null;
        url?: string | null;
        description?: string | null;
        summary?: string | null;
        tags?: string[] | null;
      },
    ): Promise<BookmarkResponse> => {
      // convert the params to a PATCH body
      const body = {
        title: params.title,
        url: params.url,
        description: params.description,
        summary: params.summary,
        tags: params.tags,
      } satisfies BookmarkUpdateRequest;

      // update the bookmark
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        const bookmark = await updateBookmark(bookmarkId, body);
        dispatch({ type: "SET_BOOKMARK", bookmark });
        return bookmark;
      } finally {
        // clear the loading flag and refresh the bookmarks list
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
        pageQueriesRef.current.clear();
        void getBookmarksPage({ offset: 0 });
      }
    },
    [getBookmarksPage],
  );

  const removeBookmark = useCallback(
    async (bookmarkId: string): Promise<void> => {
      // remove the bookmark
      try {
        dispatch({ type: "SET_IS_LOADING", isLoading: true });
        await deleteBookmark(bookmarkId);
      } finally {
        // clear the loading flag and refresh the bookmarks list
        dispatch({ type: "SET_IS_LOADING", isLoading: false });
        pageQueriesRef.current.clear();
        void getBookmarksPage({ offset: 0 });
      }
    },
    [getBookmarksPage],
  );

  const setBookmark = useCallback((bookmark: BookmarkResponse) => {
    dispatch({ type: "SET_BOOKMARK", bookmark });
  }, []);

  const setSort = useCallback((sort: Sort) => {
    dispatch({ type: "SET_SORT", sort });
  }, []);

  // memoize context to avoid rerendering consumers
  const value = useMemo(
    () => ({
      previewBookmark: getBookmarkPreview,
      addBookmark,
      saveBookmark,
      removeBookmark,
      getBookmarksPage,
      getBookmarksSearchPage,
      addRelatedBookmarks,
      setBookmark,
      setSort,
      ...state,
    }),
    [
      getBookmarkPreview,
      addBookmark,
      saveBookmark,
      removeBookmark,
      getBookmarksPage,
      getBookmarksSearchPage,
      addRelatedBookmarks,
      setBookmark,
      setSort,
      state,
    ],
  );
  return <BookmarksContext.Provider value={value}>{children}</BookmarksContext.Provider>;
}
