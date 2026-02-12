import { SubmitEventHandler, useEffect } from "react";
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
import { Sort, TagMode } from "@/features/bookmarks/providers/bookmark/BookmarksProvider";
import { TagModeSelect } from "@/components/TagModeSelect";

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
    getBookmarksSearchPage,
    search,
    setSearch,
    selectedTags,
    selectedTagMode,
    setSelectedTagMode,
  } = useBookmarks();

  // reset the list page when the search gets cleared
  useEffect(() => {
    if (!search?.trim()) {
      void getBookmarksPage({
        sort,
        offset: 0,
        tag_mode: selectedTagMode,
        // TODO: tags
      });
    }
  }, [search, sort, getBookmarksPage, selectedTagMode]);

  const onSearch: SubmitEventHandler = (event) => {
    // search bookmarks on submitting
    event.preventDefault();
    if (!search?.trim()) {
      void getBookmarksPage({
        sort,
        offset: 0,
        tag_mode: selectedTagMode,
        // TODO: tags
      });
    } else {
      void getBookmarksSearchPage({
        search: search.trim(),
        tag_mode: selectedTagMode,
        // TODO: tags
      });
    }
  };

  const onTagModeChange = (value: string) => {
    const tagMode = value as TagMode;
    setSelectedTagMode(tagMode);
    if (!search?.trim()) {
      void getBookmarksPage({
        sort,
        offset: 0,
        tag_mode: tagMode,
        // TODO: tags
      });
    } else {
      void getBookmarksSearchPage({
        search: search.trim(),
        tag_mode: tagMode,
        // TODO: tags
      });
    }
  };

  // reload the list when the sort changes
  const onSort = (sortValue: Sort) => {
    setSort(sortValue);
    void getBookmarksPage({
      search,
      sort: sortValue,
      offset: 0,
      tag_mode: selectedTagMode,
      // TODO: tags
    });
  };

  return (
    <div>
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
            disabled={!search?.trim()}
            className="absolute top-1 right-5 rounded-full cursor-pointer"
          >
            <Search />
          </Button>
        </form>
      )}
      <div className="flex items-center justify-between p-4">
        {/* tags multiselect */}
        {selectedTags.length > 0 && (
          <TagModeSelect tagMode={selectedTagMode} onChange={onTagModeChange} />
        )}

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
