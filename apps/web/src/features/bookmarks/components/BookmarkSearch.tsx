import { MouseEventHandler, SubmitEventHandler } from "react";
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
import { TagModeSelect } from "@/components/TagModeSelect";
import { TagMultiSelect } from "@/components/TagMultiSelect";
import { TagItems } from "@/components/TagItems";

interface BookmarkSearchProps {
  onAddBookmarkClick: () => void;
}

export function BookmarkSearch({ onAddBookmarkClick }: BookmarkSearchProps) {
  const {
    userHasBookmarks,
    isLoading,
    sort,
    setSort,
    getBookmarksPage,
    search,
    setSearch,
    userTags,
    selectedTags,
    setSelectedTags,
    selectedTagMode,
    setSelectedTagMode,
  } = useBookmarks();

  // search bookmarks on submitting
  const onSearch: SubmitEventHandler = (event) => {
    event.preventDefault();
    if (search?.trim()) {
      void getBookmarksPage({ search: search.trim(), offset: 0 });
    }
  };

  // search bookmarks on clearing
  const onClearSearch: MouseEventHandler = (event) => {
    event.preventDefault();
    setSearch("");
    void getBookmarksPage({ search: "", offset: 0 });
  };

  return (
    <div>
      {/* search form */}
      {userHasBookmarks && (
        <form className="relative px-4" onSubmit={onSearch}>
          <Textarea
            placeholder="Search your Bookmarks"
            disabled={isLoading}
            rows={1}
            className="
              rounded-4xl resize-none pt-2.5 pr-12
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
                if (!search?.trim()) {
                  return;
                }
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />

          {search?.trim() && (
            <button
              type="button"
              className="absolute top-2.5 right-16 cursor-pointer"
              onMouseDown={onClearSearch}
            >
              <X className="h-6 w-6 text-muted-foreground" />
            </button>
          )}
          <Button
            type="submit"
            size="icon"
            disabled={!search?.trim()}
            className="absolute top-1 right-5 rounded-full cursor-pointer"
          >
            <Search />
          </Button>
        </form>
      )}

      {/* selected tags */}
      {selectedTags.length > 0 && (
        <TagItems
          tags={selectedTags}
          onChange={setSelectedTags}
          canSelect={true}
          className="px-5 pt-4"
        />
      )}

      <div
        className="
          flex flex-col
          gap-4 p-4
          sm:flex-row! sm:items-center! sm:justify-between!
        "
      >
        {/* tag select */}
        {userTags.length > 0 && (
          <div className="flex items-center gap-2">
            <TagMultiSelect userTags={userTags} tags={selectedTags} onChange={setSelectedTags} />
            <TagModeSelect tagMode={selectedTagMode} onChange={setSelectedTagMode} />
          </div>
        )}

        {/* sort select */}
        {userHasBookmarks && !search?.trim() ? (
          <div className="flex items-center gap-2">
            Sort by:
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger className="w-fit cursor-pointer bg-accent/50 hover:bg-accent">
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
