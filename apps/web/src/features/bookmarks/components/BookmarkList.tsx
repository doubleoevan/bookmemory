import { BookmarkListItem } from "@/features/bookmarks/components/BookmarkListItem";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { useEffect, useRef } from "react";
import { BookmarkResponse } from "@bookmemory/contracts";
import { Loader } from "@/components/Loader";

interface BookmarkListProps {
  onAddBookmarkClick: () => void;
  onBookmarkClick: () => void;
}

export function BookmarkList({ onAddBookmarkClick, onBookmarkClick }: BookmarkListProps) {
  const {
    userHasBookmarks,
    getBookmarksPage,
    isLoading,
    bookmarks,
    total,
    sort,
    selectedTags,
    selectedTagMode,
  } = useBookmarks();

  // update the bookmarks when the tag or sort filters change
  useEffect(() => {
    void getBookmarksPage({ offset: 0 });

    // keep this hook stable
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTags, selectedTagMode, sort]);

  // infinite scroll with a page bottom sentinel
  const hasMoreBookmarks = total > 0 && bookmarks.length < total;
  const scrollAreaRef = useRef<HTMLElement | null>(null);
  const scrollBottomRef = useRef<HTMLLIElement | null>(null);
  useEffect(() => {
    const scrollAreaElement = scrollAreaRef.current;
    const scrollBottomElement = scrollBottomRef.current;
    if (!scrollAreaElement || !scrollBottomElement || !hasMoreBookmarks || isLoading) {
      return;
    }

    // load the next page when the bottom sentinel becomes visible
    const pageBottomObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          pageBottomObserver.unobserve(scrollBottomElement);
          void getBookmarksPage();
        }
      },
      { root: scrollAreaElement, rootMargin: "0px", threshold: 0 },
    );
    pageBottomObserver.observe(scrollBottomElement);

    // disconnect the page bottom observer when the component unmounts
    return () => pageBottomObserver.disconnect();
  }, [getBookmarksPage, isLoading, hasMoreBookmarks]);

  // show the loader while loading initial bookmarks
  if (isLoading && !userHasBookmarks) {
    return <Loader className="w-[10vw] h-[10dvh]" />;
  }

  // show a prompt if the user has no bookmarks yet
  if (!isLoading && !userHasBookmarks) {
    return (
      <h1
        className="
          flex flex-col
          items-center justify-center
          text-2xl text-muted-foreground
          cursor-pointer
        "
        onClick={onAddBookmarkClick}
      >
        Add a bookmark to get started...
      </h1>
    );
  }

  // show the bookmarks list
  return (
    <section ref={scrollAreaRef} aria-label="Saved bookmarks" className="h-[75dvh] overflow-y-auto">
      <ul className=" ">
        {bookmarks.map((bookmark: BookmarkResponse) => (
          <li key={bookmark.id} className="py-2">
            <BookmarkListItem bookmark={bookmark} onBookmarkClick={onBookmarkClick} />
          </li>
        ))}

        {/* sentinel: last list item, triggers loading the next page */}
        {hasMoreBookmarks && <li ref={scrollBottomRef} aria-hidden="true" className="h-1" />}
      </ul>
    </section>
  );
}
