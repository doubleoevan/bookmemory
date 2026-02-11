import { useState } from "react";
import { Search, X } from "lucide-react";
import { Button, Textarea } from "@bookmemory/ui";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";

interface BookmarkSearchProps {
  onAddBookmarkClick: () => void;
}

export function BookmarkSearch({ onAddBookmarkClick }: BookmarkSearchProps) {
  const [search, setSearch] = useState("");
  const { userHasBookmarks, isLoading } = useBookmarks();
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
        {userHasBookmarks ? <div>Tags Multiselect</div> : <div />}
        {userHasBookmarks ? <div>Sort Dropdown</div> : <div />}
        <Button onClick={onAddBookmarkClick}>Add Bookmark</Button>
      </div>
    </div>
  );
}
