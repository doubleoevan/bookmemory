import { ExternalLink as ExternalLinkIcon, Eye } from "lucide-react";
import {
  Badge,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@bookmemory/ui";
import { ExternalLink } from "@/components/ExternalLink";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";

interface EditBookmarkModalProps {
  onClose: () => void;
  onView: () => void;
}

export function EditBookmarkModal({ onClose, onView }: EditBookmarkModalProps) {
  const { bookmark } = useBookmarks();

  return (
    <Dialog
      open
      onOpenChange={(isOpening) => {
        if (!isOpening) {
          onClose();
        }
      }}
    >
      <DialogContent
        className="
          w-[80vw] h-[80vh] max-w-4xl
          flex flex-col
          overflow-y-auto
        "
      >
        <DialogHeader>
          <DialogTitle className="flex items-center justify-center gap-1 text-muted-foreground">
            Edit Bookmark
            <Eye className="w-4 h-4 cursor-pointer" onClick={onView} />
          </DialogTitle>
          {bookmark?.description && (
            <DialogDescription className="sr-only">{bookmark.description}</DialogDescription>
          )}
        </DialogHeader>
        {bookmark?.url && (
          <div>
            <span className="text-muted-foreground">URL: </span>
            <ExternalLink href={bookmark.url} className="inline-flex items-center gap-1">
              {bookmark.url} <ExternalLinkIcon className="w-4 h-4" />
            </ExternalLink>
          </div>
        )}
        <h1>
          <span className="text-muted-foreground">Title: </span>
          {bookmark?.title}
        </h1>
        <h2 className="flex justify-center text-muted-foreground">Description</h2>
        <p>{bookmark?.description}</p>
        <h2 className="flex justify-center text-muted-foreground">Summary</h2>
        <p>{bookmark?.summary}</p>
        <div className="flex flex-wrap gap-2">
          <span className="text-muted-foreground">Tags:</span>
          {bookmark?.tags?.map((tag) => (
            <Badge key={tag.id} variant="secondary">
              {tag.name}
            </Badge>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
