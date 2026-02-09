import { BookmarkSearch } from "@/features/bookmarks/components/BookmarkSearch";
import { BookmarkList } from "@/features/bookmarks/components/BookmarkList";

export function BookmarksHome() {
  return (
    <div className="mx-auto w-full max-w-4xl p-4">
      <BookmarkSearch />
      <BookmarkList />
    </div>
  );
}
