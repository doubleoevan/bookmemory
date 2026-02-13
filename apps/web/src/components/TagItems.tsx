import { ReactNode } from "react";
import { X } from "lucide-react";
import { Badge, cn } from "@bookmemory/ui";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";

export function TagItems({
  tags,
  label,
  onChange,
  canSelect = false,
  className,
}: {
  tags: string[];
  label?: ReactNode;
  onChange?: (next: string[]) => void;
  canSelect?: boolean;
  className?: string;
}) {
  const { setSelectedTags, setSelectedTagMode } = useBookmarks();

  // filter bookmarks to the selected tag
  const onSelectTag = (tag: string) => {
    if (canSelect) {
      setSelectedTags([tag]);
      setSelectedTagMode("all");
    }
  };

  // return the tags with the selected tag removed
  function onRemoveTag(name: string) {
    onChange?.(tags.filter((tag) => tag !== name));
  }

  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {label}
      {tags.map((tag) => (
        <Badge key={tag} variant="secondary" className="flex items-center gap-2 outline">
          <button
            className={cn(canSelect && "cursor-pointer")}
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelectTag(tag);
            }}
          >
            {tag}
          </button>
          {onChange && (
            <button type="button" onClick={() => onRemoveTag(tag)} className="cursor-pointer">
              <X className="w-3 h-3" />
            </button>
          )}
        </Badge>
      ))}
    </div>
  );
}
