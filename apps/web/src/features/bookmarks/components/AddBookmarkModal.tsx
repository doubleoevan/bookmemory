import {
  cn,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@bookmemory/ui";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { SubmitEventHandler, useState } from "react";
import { Loader } from "@/components/Loader";
import { isUrlValid } from "@/utils/url";

interface AddBookmarkModalProps {
  onClose: () => void;
  onEdit: () => void;
}

export function AddBookmarkModal({ onClose, onEdit }: AddBookmarkModalProps) {
  const [bookmarkType, setBookmarkType] = useState<"link" | "note" | "file">("link");
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const { previewBookmark, isLoading } = useBookmarks();

  const onPreview: SubmitEventHandler = async (event) => {
    event.preventDefault();

    // set the preview bookmark then forward to the edit view
    if (!isUrlValid(url)) {
      setError("Please paste a valid URL");
      return;
    }

    // load the bookmark preview and forward to the edit view
    await previewBookmark({ url, type: bookmarkType });
    onEdit();
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
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {isLoading ? "Loading your bookmark..." : error ? error : "New Bookmark"}
          </DialogTitle>
        </DialogHeader>
        {isLoading ? (
          <div>
            <Loader className="w-10 h-10" />
          </div>
        ) : (
          <form className="relative flex gap-2" onSubmit={onPreview}>
            {/* url input */}
            {bookmarkType === "link" && (
              <Input
                type="text"
                placeholder="Paste your link here and press Enter"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                className={cn(error ? "focus-visible:ring-destructive" : "")}
              />
            )}

            {/* bookmark type select */}
            <Select
              value={bookmarkType}
              onValueChange={(value) => setBookmarkType(value as "link" | "note" | "file")}
            >
              <SelectTrigger className="w-fit cursor-pointer">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem className="cursor-pointer" value="link">
                  Link
                </SelectItem>
                <SelectItem className="cursor-not-allowed" disabled value="file">
                  File
                </SelectItem>
                <SelectItem className="cursor-not-allowed" disabled value="note">
                  Note
                </SelectItem>
              </SelectContent>
            </Select>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
