import { BookmarkResponse } from "@bookmemory/contracts";

export function BookmarkListItem({ bookmark }: { bookmark: BookmarkResponse }) {
  return (
    <article className="py-4">
      <h2>{bookmark.title}</h2>
    </article>
  );
}
