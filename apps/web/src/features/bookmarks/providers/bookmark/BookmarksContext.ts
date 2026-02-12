import { createContext } from "react";
import {
  BookmarkState,
  Sort,
  TagMode,
} from "@/features/bookmarks/providers/bookmark/BookmarksProvider";
import { BookmarkResponse, TagCountResponse } from "@bookmemory/contracts";

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

  removeBookmark: (bookmarkId: string) => Promise<void>;
  refreshBookmark: (bookmarkId: string) => Promise<void>;

  getBookmarksPage: (params?: {
    search?: string | null;
    tag?: string[];
    tag_mode?: "any" | "all" | "ignore";
    sort?: Sort;
    limit?: number;
    offset?: number;
  }) => Promise<void>;

  getBookmarksSearchPage: (params: {
    search: string;
    tag?: string[];
    tag_mode?: "any" | "all" | "ignore";
    limit?: number;
  }) => Promise<void>;

  addRelatedBookmarks: (params: {
    bookmarkId: string;
    tag_mode?: "any" | "all" | "ignore";
    limit?: number;
  }) => Promise<void>;

  setBookmark: (bookmark: BookmarkResponse) => void;
  setSearch: (search: string) => void;
  setSort: (sort: Sort) => void;
  getUserTags: () => Promise<TagCountResponse[]>;
  setSelectedTags: (selectedTags: string[]) => void;
  setSelectedTagMode: (selectedTagMode: TagMode) => void;
};

export const BookmarksContext = createContext<BookmarkContextValue | null>(null);
