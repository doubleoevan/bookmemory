import { BookmarkListItem } from "@/features/bookmarks/components/BookmarkListItem";

export function BookmarkList() {
  return (
    <div>
      <BookmarkListItem key={1} />
      <BookmarkListItem key={2} />
      <BookmarkListItem key={3} />
    </div>
  );
}
