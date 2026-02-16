import Highlighter from "react-highlight-words";
import { ExternalLink as ExternalLinkIcon } from "lucide-react";
import { BookmarkResponse, BookmarkSearchResponse } from "@bookmemory/contracts";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { ExternalLink } from "@/components/ExternalLink";
import { getDomain } from "@/utils/url";
import { TagItems } from "@/components/TagItems";

function toSearchWords(search: string | undefined | null): string[] {
  const trimmedSearch = search?.trim() ?? "";
  if (!trimmedSearch) return [];

  const searchWords = trimmedSearch.split(/\s+/).filter(Boolean);
  return [trimmedSearch, ...searchWords];
}

export function BookmarkListItem({
  bookmark,
  onBookmarkClick,
}: {
  bookmark: BookmarkResponse | BookmarkSearchResponse;
  onBookmarkClick: (() => void) | undefined;
}) {
  const { setBookmark, search } = useBookmarks();
  const searchWords = toSearchWords(search);
  const snippet = "snippet" in bookmark ? bookmark.snippet : null;
  const tags = bookmark.tags?.map((tag) => tag.name) || [];

  // show the selected bookmark on click
  const onViewBookmark = () => {
    setBookmark(bookmark);
    onBookmarkClick?.();
  };

  return (
    <article
      className="
        p-4
        rounded-md
        hover:bg-accent hover:border-input
        cursor-pointer
        leading-relaxed
      "
      onClick={onViewBookmark}
    >
      <h2 className="break-word wrap-anywhere">
        {bookmark.url ? (
          <ExternalLink href={bookmark.url} className="inline-flex items-center gap-1">
            {bookmark.title} <ExternalLinkIcon className="w-4 h-4" />
          </ExternalLink>
        ) : (
          <Highlighter
            searchWords={searchWords} // or split into keywords
            textToHighlight={bookmark.title}
            highlightClassName="bg-yellow-200 dark:bg-yellow-700"
          />
        )}
      </h2>

      {bookmark.url && (
        <div className="text-xs text-muted-foreground">{getDomain(bookmark.url)}</div>
      )}

      {snippet ? (
        <p className="text-muted-foreground line-clamp-4">
          <Highlighter
            searchWords={searchWords} // or split into keywords
            textToHighlight={snippet}
            highlightClassName="bg-yellow-200 dark:bg-yellow-700"
          />
        </p>
      ) : (
        <p className="text-muted-foreground line-clamp-2">
          <Highlighter
            searchWords={searchWords} // or split into keywords
            textToHighlight={bookmark.description ?? ""}
            highlightClassName="bg-yellow-200 dark:bg-yellow-700"
          />
        </p>
      )}
      {tags.length > 0 && <TagItems tags={tags} canSelect={true} />}
    </article>
  );
}
