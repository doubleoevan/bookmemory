import { ExternalLink as ExternalLinkIcon } from "lucide-react";
import { Badge } from "@bookmemory/ui";
import { BookmarkResponse } from "@bookmemory/contracts";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { ExternalLink } from "@/components/ExternalLink";
import { getDomain } from "@/utils/url";

export function BookmarkListItem({
  bookmark,
  onBookmarkClick,
}: {
  bookmark: BookmarkResponse;
  onBookmarkClick: (() => void) | undefined;
}) {
  const { setBookmark } = useBookmarks();
  const onClick = () => {
    setBookmark(bookmark);
    onBookmarkClick?.();
  };
  return (
    <article
      className="
        p-4
        rounded-md
        hover:bg-accent/50 hover:border-input
        cursor-pointer
        leading-relaxed
      "
      onClick={onClick}
    >
      <h2>
        {bookmark.url ? (
          <ExternalLink href={bookmark.url} className="inline-flex items-center gap-1">
            {bookmark.title} <ExternalLinkIcon className="w-4 h-4" />
          </ExternalLink>
        ) : (
          bookmark.title
        )}
      </h2>
      {bookmark.url && (
        <div className="text-xs text-muted-foreground">{getDomain(bookmark.url)}</div>
      )}
      <p className="text-muted-foreground truncate">{bookmark.description}</p>
      <div className="flex flex-wrap gap-2">
        {bookmark?.tags?.map((tag) => (
          <Badge key={tag.id} variant="secondary">
            {tag.name}
          </Badge>
        ))}
      </div>
    </article>
  );
}
