import { createContext } from "react";
import { BookmarkState } from "@/features/bookmarks/providers/bookmark/BookmarkProvider";
import { BookmarkResponse } from "@bookmemory/contracts";

export type BookmarkContextValue = BookmarkState & {
  setBookmark: (bookmark: BookmarkResponse) => void;
};

export const BookmarkContext = createContext<BookmarkContextValue | null>(null);
