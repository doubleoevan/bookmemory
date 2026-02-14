import { ExternalLink as ExternalLinkIcon } from "lucide-react";
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@bookmemory/ui";
import { ExternalLink } from "@/components/ExternalLink";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { getDomain } from "@/utils/url";

interface RemoveBookmarkModalProps {
  onEdit: () => void;
  onClose: () => void;
}

export function RemoveBookmarkModal({ onEdit, onClose }: RemoveBookmarkModalProps) {
  const { bookmark, removeBookmark } = useBookmarks();

  const onRemove = async () => {
    // remove the bookmark from the database and close the modal
    const bookmarkId = bookmark?.id;
    if (bookmarkId) {
      await removeBookmark(bookmarkId);
    }
    onClose();
  };

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
          w-[50vw] max-w-4xl
          flex flex-col
          overflow-y-auto
          leading-4
        "
      >
        <DialogHeader>
          <DialogTitle className="flex items-center justify-center gap-1 text-muted-foreground">
            Remove this Bookmark?
          </DialogTitle>
          {bookmark?.description && (
            <DialogDescription className="sr-only">{bookmark.description}</DialogDescription>
          )}
        </DialogHeader>
        <h2>
          {bookmark?.url ? (
            <ExternalLink href={bookmark.url} className="inline-flex items-center gap-1">
              {bookmark.title} <ExternalLinkIcon className="w-4 h-4" />
            </ExternalLink>
          ) : (
            bookmark?.title
          )}
        </h2>
        {bookmark?.url && (
          <div className="text-xs text-muted-foreground">{getDomain(bookmark.url)}</div>
        )}
        <div className="flex justify-end gap-2">
          <Button className="w-fit" onClick={onEdit}>
            Cancel
          </Button>
          <Button
            className="w-fit outline bg-muted hover:bg-destructive"
            variant="ghost"
            onClick={onRemove}
          >
            Remove
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
