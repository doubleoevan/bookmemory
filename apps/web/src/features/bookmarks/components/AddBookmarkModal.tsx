import {
  Button,
  cn,
  Dialog,
  DialogContent,
  DialogDescription,
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
import { isUrlValid, normalizeUrl } from "@/utils/url";
import { Plus } from "lucide-react";

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

    // normalize and validate the url
    const normalizedUrl = normalizeUrl(url);
    if (!isUrlValid(normalizedUrl)) {
      setError("Please paste a valid URL");
      return;
    }

    // load the bookmark preview then forward to the edit view
    await previewBookmark({ url: normalizedUrl, type: bookmarkType });
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
      <DialogContent
        className="
          top-[20%] left-1/2 -translate-x-1/2 translate-y-0
          max-w-[95vw] sm:max-w-4xl!
        "
      >
        <DialogHeader>
          <DialogTitle>
            {isLoading ? "Loading your bookmark..." : error ? error : "New Bookmark"}
          </DialogTitle>
          <DialogDescription className="sr-only">
            {isLoading ? "Loading your bookmark..." : "Add New Bookmark"}
          </DialogDescription>
        </DialogHeader>
        {isLoading ? (
          <div>
            <Loader className="w-10 h-10" />
          </div>
        ) : (
          <form className="flex gap-2 relative" onSubmit={onPreview}>
            {/* url input */}
            {bookmarkType === "link" && (
              <Input
                type="text"
                placeholder="Paste your link here and press Enter"
                value={url}
                required
                onInvalid={(event) => {
                  event.currentTarget.setCustomValidity("Please provide a bookmark link.");
                }}
                onInput={(event) => {
                  event.currentTarget.setCustomValidity("");
                }}
                onChange={(event) => setUrl(event.target.value)}
                className={cn("rounded-md", error ? "focus-visible:ring-destructive" : "")}
              />
            )}

            <Button
              type="submit"
              size="icon"
              disabled={!url?.trim()}
              className="
                absolute top-1
                right-1 sm:right-20!
                rounded-sm
                w-7 h-7
                cursor-pointer
              "
            >
              <Plus />
            </Button>

            {/* bookmark type select */}
            <div className="hidden sm:inline!">
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
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
