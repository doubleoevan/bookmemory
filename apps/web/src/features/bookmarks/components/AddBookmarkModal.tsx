import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@bookmemory/ui";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";

interface AddBookmarkModalProps {
  onClose: () => void;
  onEdit: () => void;
}

export function AddBookmarkModal({ onClose }: AddBookmarkModalProps) {
  const { addBookmark } = useBookmarks();
  console.log(addBookmark);
  return (
    <Dialog
      open
      onOpenChange={(isOpening) => {
        if (!isOpening) {
          onClose();
        }
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Bookmark</DialogTitle>
        </DialogHeader>
        <div>Add Bookmark Modal</div>
      </DialogContent>
    </Dialog>
  );
}
