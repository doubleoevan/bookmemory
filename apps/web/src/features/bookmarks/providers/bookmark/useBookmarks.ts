import { useContext } from "react";
import { type BookmarkContextValue } from "@/features/bookmarks/providers/bookmark/index";
import { BookmarksContext } from "@/features/bookmarks/providers/bookmark/BookmarksContext";

export function useBookmarks(): BookmarkContextValue {
  const context = useContext(BookmarksContext);
  if (!context) {
    throw new Error("useBookmarks must be used within <BookmarksProvider />");
  }
  return context;
}
