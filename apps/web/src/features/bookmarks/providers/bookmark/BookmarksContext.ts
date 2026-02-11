import { createContext } from "react";
import { BookmarkState } from "@/features/bookmarks/providers/bookmark/BookmarksProvider";
import { BookmarkResponse } from "@bookmemory/contracts";

export type BookmarkContextValue = BookmarkState & {
  getBookmarksPage: (params?: {
    search?: string | null;
    tag?: string[];
    tag_mode?: "any" | "all" | "ignore";
    sort?: "alphabetical" | "recent";
    limit?: number;
  }) => Promise<void>;

  addRelatedBookmarks: (params: {
    bookmarkId: string;
    tag_mode?: "any" | "all" | "ignore";
    limit?: number;
  }) => Promise<void>;

  setBookmark: (bookmark: BookmarkResponse) => void;
};

export const BookmarksContext = createContext<BookmarkContextValue | null>(null);
