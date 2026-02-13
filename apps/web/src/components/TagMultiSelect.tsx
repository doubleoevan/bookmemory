import { ReactNode, useMemo, useState } from "react";
import {
  cn,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@bookmemory/ui";
import { Check, Plus } from "lucide-react";
import { TagCountResponse } from "@bookmemory/contracts";

export function TagMultiSelect({
  tags,
  userTags,
  onChange,
  canCreate = false,
  className,
}: {
  tags: string[];
  userTags: TagCountResponse[];
  onChange: (next: string[]) => void;
  canCreate?: boolean; // not used yet
  children?: ReactNode;
  className?: string;
}) {
  const [tagSearch, setTagSearch] = useState("");
  const [openSearchMenu, setOpenSearchMenu] = useState(false);

  // show all options that match the tag search
  const searchTags = useMemo(() => {
    // show all tags if the search is empty
    const search = tagSearch.toLowerCase();
    if (!search) {
      return userTags;
    }

    // return only tags that match the search
    return userTags.filter((tag) => tag.name.toLowerCase().includes(search));
  }, [tagSearch, userTags]);

  // add or remove selected tags
  const onTagSelect = (name: string) => {
    if (tags.includes(name)) {
      onChange(tags.filter((tag) => tag !== name));
    } else {
      onChange([...tags, name]);
    }
  };

  // determine if a tag can be added
  const searchTag = tagSearch.trim();
  const canAddTag = useMemo(() => {
    // check if the select is in create mode
    if (!canCreate) {
      return false;
    }

    // check if the tag name is valid
    if (!searchTag) {
      return false;
    }

    // check if the tag was already created
    const isTagExisting = userTags.some(
      (tag) => tag.name.toLowerCase() === searchTag.toLowerCase(),
    );
    if (isTagExisting) {
      return false;
    }

    // check if the tag was already selected
    return !tags.some((tag) => tag.toLowerCase() === searchTag.toLowerCase());
  }, [canCreate, searchTag, userTags, tags]);

  // add a new tag
  const onAddTag = () => {
    // check if the tag can be added
    if (!canAddTag) {
      return;
    }

    // add the new tag, clear the search, and close the menu
    onChange([...tags, searchTag]);
    setTagSearch("");
    setOpenSearchMenu(false);
  };

  return (
    <div className={className}>
      {/* tag selector */}
      <Popover
        open={openSearchMenu}
        onOpenChange={(open) => {
          // clear the search when the menu is closed
          setOpenSearchMenu(open);
          if (!open) {
            setTagSearch("");
          }
        }}
      >
        {/* select tags button */}
        <PopoverTrigger asChild>
          <button
            type="button"
            className="
              rounded-lg border
              px-4 py-1
              bg-accent/50 hover:bg-accent
              cursor-pointer
            "
          >
            Select Tags
          </button>
        </PopoverTrigger>

        {/* search tags menu */}
        <PopoverContent align="start" className="rounded-lg border p-0">
          <Command>
            <CommandInput
              placeholder="Search tags..."
              value={tagSearch}
              onValueChange={setTagSearch}
              onKeyDown={(event) => {
                // try to add on Enter
                if (event.key !== "Enter") {
                  return;
                }

                // check if there are no other tags available
                if (!canAddTag || searchTags.length > 0) {
                  return;
                }

                // add the new tag
                event.preventDefault();
                event.stopPropagation();
                onAddTag();
              }}
            />
            {!canAddTag && <CommandEmpty>No tags</CommandEmpty>}
            <CommandGroup>
              {canAddTag && (
                <CommandItem
                  value={`create:${searchTag.toLowerCase()}`}
                  onSelect={onAddTag}
                  className="cursor-pointer"
                >
                  <div className="flex w-full items-center gap-2">
                    <Plus className="h-4 w-4" />
                    <span>Create "{searchTag}"</span>
                  </div>
                </CommandItem>
              )}

              {searchTags.map((tag) => {
                const isTagSelected = tags.includes(tag.name);
                return (
                  <CommandItem
                    key={tag.name}
                    onSelect={() => onTagSelect(tag.name)}
                    className="cursor-pointer"
                  >
                    <div className="flex w-full items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Check
                          className={cn("h-4 w-4", isTagSelected ? "opacity-100" : "opacity-0")}
                        />
                        <span>{tag.name}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">{tag.count}</span>
                    </div>
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
