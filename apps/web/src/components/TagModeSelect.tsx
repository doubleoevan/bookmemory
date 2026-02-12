import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@bookmemory/ui";
import { TagMode } from "@/features/bookmarks/providers/bookmark/BookmarksProvider";

export function TagModeSelect({
  tagMode,
  onChange,
}: {
  tagMode: TagMode;
  onChange: (mode: TagMode) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      Match tags:
      <Select value={tagMode} onValueChange={onChange}>
        <SelectTrigger className="w-fit cursor-pointer">
          <SelectValue placeholder="Match tags" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem className="cursor-pointer" value="any">
            Any
          </SelectItem>
          <SelectItem className="cursor-pointer" value="all">
            All
          </SelectItem>
          <SelectItem className="cursor-pointer" value="ignore">
            None
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
