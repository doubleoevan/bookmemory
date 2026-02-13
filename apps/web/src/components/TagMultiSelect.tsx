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
import { Check } from "lucide-react";
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
  console.log("TODO: implement", { canCreate });
  const [tagSearch, setTagSearch] = useState("");
  const [openSearchMenu, setOpenSearchMenu] = useState(false);

  // show all options that match the tag search
  const searchTagOptions = useMemo(() => {
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

  return (
    <div className={className}>
      {/* tag selector */}
      <Popover open={openSearchMenu} onOpenChange={setOpenSearchMenu}>
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
            />
            <CommandEmpty>No tags yet.</CommandEmpty>
            <CommandGroup>
              {searchTagOptions.map((tag) => {
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
