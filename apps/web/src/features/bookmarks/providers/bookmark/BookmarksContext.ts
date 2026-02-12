import { createContext } from "react";
import { BookmarkState, Sort } from "@/features/bookmarks/providers/bookmark/BookmarksProvider";
import { BookmarkResponse } from "@bookmemory/contracts";

export type BookmarkContextValue = BookmarkState & {
  previewBookmark: (params: {
    url: string;
    type?: "link" | "note" | "file";
  }) => Promise<BookmarkResponse>;

  addBookmark: (params: {
    title: string;
    description: string;
    url?: string | null;
    type?: "link" | "note" | "file";
    tags?: string[];

    // allow extra fields to be passed
    [key: string]: unknown;
  }) => Promise<BookmarkResponse>;

  saveBookmark: (
    bookmarkId: string,
    params: {
      title?: string | null;
      url?: string | null;
      description?: string | null;
      summary?: string | null;
      tags?: string[] | null;

      // allow extra fields to be passed
      [key: string]: unknown;
    },
  ) => Promise<BookmarkResponse>;

  removeBookmark: (bookmarkId: string) => Promise<BookmarkResponse>;

  getBookmarksPage: (params?: {
    search?: string | null;
    tag?: string[];
    tag_mode?: "any" | "all" | "ignore";
    sort?: Sort;
    limit?: number;
    offset?: number;
  }) => Promise<void>;

  addRelatedBookmarks: (params: {
    bookmarkId: string;
    tag_mode?: "any" | "all" | "ignore";
    limit?: number;
  }) => Promise<void>;

  setBookmark: (bookmark: BookmarkResponse) => void;
  setSort: (sort: Sort) => void;
};

export const BookmarksContext = createContext<BookmarkContextValue | null>(null);
