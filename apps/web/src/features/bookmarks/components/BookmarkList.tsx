import { BookmarkListItem } from "@/features/bookmarks/components/BookmarkListItem";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { useEffect, useRef } from "react";
import { BookmarkResponse } from "@bookmemory/contracts";
import { Loader } from "@/components/Loader";

export function BookmarkList() {
  const { getBookmarksPage, isLoading, bookmarks, total } = useBookmarks();

  // load initial bookmarks on mount
  useEffect(() => {
    if (bookmarks.length === 0) {
      void getBookmarksPage();
    }
  }, [bookmarks.length, getBookmarksPage]);

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
  if (isLoading && !bookmarks.length) {
    return <Loader className="w-[10vh] h-[10vh]" />;
  }

  // show the bookmarks list
  return (
    <section ref={scrollAreaRef} aria-label="Saved bookmarks" className="h-[80vh] overflow-y-auto">
      <ul className="divide-y divide-border">
        {bookmarks.map((bookmark: BookmarkResponse) => (
          <li key={bookmark.id}>
            <BookmarkListItem bookmark={bookmark} />
          </li>
        ))}

        {/* sentinel: last list item, triggers loading the next page */}
        {hasMoreBookmarks && <li ref={scrollBottomRef} aria-hidden="true" className="h-1" />}
      </ul>
    </section>
  );
}
