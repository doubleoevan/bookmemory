import { useState } from "react";
import { Search, X } from "lucide-react";
import {
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from "@bookmemory/ui";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { Sort } from "@/features/bookmarks/providers/bookmark/BookmarksProvider";

interface BookmarkSearchProps {
  onAddBookmarkClick: () => void;
}

export function BookmarkSearch({ onAddBookmarkClick }: BookmarkSearchProps) {
  const [search, setSearch] = useState("");
  const { userHasBookmarks, isLoading, sort, setSort, getBookmarksPage } = useBookmarks();

  // reload the list when the sort changes
  const onSort = (sortValue: Sort) => {
    setSort(sortValue);
    void getBookmarksPage({
      search,
      sort: sortValue,
      offset: 0,
      // tag, tag_mode
    });
  };

  return (
    <div>
      {userHasBookmarks && (
        <form
          className="relative px-4"
          onSubmit={(event) => {
            // search bookmarks on submitting
            event.preventDefault();
            if (!search.trim()) {
              return;
            }
          }}
        >
          <Textarea
            placeholder="Search your Bookmarks"
            disabled={isLoading}
            rows={1}
            className="
              rounded-[20px] resize-none pt-2.5 pr-12
              min-h-11 max-h-50
              overflow-hidden
              bg-accent/50
              hover:bg-accent
              cursor-pointer
            "
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault(); // submit on enter
                if (!search.trim()) {
                  return;
                }
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />

          {search?.length > 0 && (
            <button
              type="button"
              className="absolute top-2.5 right-16 cursor-pointer"
              onMouseDown={(event) => {
                event.preventDefault();
                setSearch("");
              }}
            >
              <X className="h-6 w-6 text-muted-foreground" />
            </button>
          )}
          <Button
            type="submit"
            size="icon"
            disabled={!search.trim()}
            className="absolute top-1 right-5 rounded-full cursor-pointer"
          >
            <Search />
          </Button>
        </form>
      )}
      <div className="flex items-center justify-between p-4">
        {/* tags multiselect */}
        {userHasBookmarks ? <div>Tags Multiselect</div> : <div />}

        {/* sort select */}
        {userHasBookmarks && !search?.trim() ? (
          <div className="flex items-center gap-2">
            Sort by:
            <Select value={sort} onValueChange={onSort}>
              <SelectTrigger className="w-fit cursor-pointer">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem className="cursor-pointer" value="recent">
                  Recent
                </SelectItem>
                <SelectItem className="cursor-pointer" value="alphabetical">
                  Alphabetical
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        ) : (
          <div />
        )}
        {/* add bookmark button */}
        <Button onClick={onAddBookmarkClick}>Add Bookmark</Button>
      </div>
    </div>
  );
}
