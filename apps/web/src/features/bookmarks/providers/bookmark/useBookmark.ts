import { useContext } from "react";
import { type BookmarkContextValue } from "@/features/bookmarks/providers/bookmark/index";
import { BookmarkContext } from "@/features/bookmarks/providers/bookmark/BookmarkContext";

export function useBookmark(): BookmarkContextValue {
  const context = useContext(BookmarkContext);
  if (!context) {
    throw new Error("useBookmark must be used within <BookmarkProvider />");
  }
  return context;
}
