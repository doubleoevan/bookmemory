import { ExternalLink as ExternalLinkIcon, Eye } from "lucide-react";
import {
  Badge,
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Input,
  Textarea,
} from "@bookmemory/ui";
import { ExternalLink } from "@/components/ExternalLink";
import { useBookmarks } from "@/features/bookmarks/providers/bookmark";
import { SubmitEventHandler, useState } from "react";

interface EditBookmarkModalProps {
  onClose: () => void;
  onView: () => void;
  onDelete: () => void;
}

export function EditBookmarkModal({ onClose, onView, onDelete }: EditBookmarkModalProps) {
  const { bookmark, addBookmark, saveBookmark, getBookmarksPage } = useBookmarks();
  const [title, setTitle] = useState<string>(bookmark?.title ?? "");
  const [summary, setSummary] = useState<string>(bookmark?.summary ?? "");
  const [description, setDescription] = useState<string>(bookmark?.description ?? "");

  const onSave: SubmitEventHandler = async (event) => {
    event.preventDefault();

    // validate the title. should be unnecessary because the input is required.
    const bookmarkTitle = title.trim();
    if (!bookmarkTitle) {
      alert("Please enter a title");
      return;
    }

    // validate the description. should be unnecessary because the textarea is required.
    const bookmarkDescription = description.trim();
    if (!bookmarkDescription) {
      alert("Please enter a description");
      return;
    }

    // validate the summary. should be unnecessary because the textarea is required.
    const bookmarkSummary = summary.trim();
    const isBookmarkPreview = bookmark?.preview_method;
    if (!bookmarkSummary && !isBookmarkPreview) {
      alert("Please enter a summary");
      return;
    }

    // add a new bookmark if it is a preview
    if (isBookmarkPreview) {
      await addBookmark({
        ...bookmark,
        title: bookmarkTitle,
        description: bookmarkDescription,
        type: bookmark?.type as "link" | "note" | "file" | undefined, // only if your update params include type
        tags: bookmark?.tags?.map((tag) => tag.name),
      });

      // view the bookmark and refresh the bookmarks list
      onView(); // this will populate the bookmark summary
      void getBookmarksPage({ offset: 0 });
      return;
    }

    // update a bookmark if it already exists
    const bookmarkId = bookmark?.id;
    if (bookmarkId) {
      await saveBookmark(bookmarkId, {
        ...bookmark,
        title: bookmarkTitle,
        description: bookmarkDescription,
        summary: bookmarkSummary,
        type: bookmark?.type as "link" | "note" | "file" | undefined, // only if your update params include type
        tags: bookmark?.tags?.map((tag) => tag.name),
      });
    }

    // close the modal and refresh the bookmarks list
    onClose();
    void getBookmarksPage({ offset: 0 });
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
        <form onSubmit={onSave} className="flex flex-col flex-1 min-h-0 gap-4">
          {bookmark?.url && (
            <div>
              <span className="text-muted-foreground">URL: </span>
              <ExternalLink href={bookmark.url} className="inline-flex items-center gap-1">
                {bookmark.url} <ExternalLinkIcon className="w-4 h-4" />
              </ExternalLink>
            </div>
          )}
          <h2 className="text-muted-foreground">Title: </h2>
          <Input
            required
            onInvalid={(event) => {
              event.currentTarget.setCustomValidity("Please provide a bookmark title.");
            }}
            onInput={(event) => {
              event.currentTarget.setCustomValidity("");
            }}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <h2 className="text-muted-foreground">Description: </h2>
          <div className="flex flex-col flex-1 min-h-0">
            <Textarea
              value={description}
              className="flex-1 resize-none"
              required
              onInvalid={(event) => {
                event.currentTarget.setCustomValidity("Please provide a bookmark description.");
              }}
              onInput={(event) => {
                event.currentTarget.setCustomValidity("");
              }}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          {!bookmark?.preview_method && (
            <>
              <h2 className="text-muted-foreground">Summary: </h2>
              <div className="flex flex-col flex-1 min-h-0">
                <Textarea
                  value={summary}
                  className="flex-1 resize-none"
                  required
                  onInvalid={(event) => {
                    event.currentTarget.setCustomValidity("Please provide a bookmark summary.");
                  }}
                  onInput={(event) => {
                    event.currentTarget.setCustomValidity("");
                  }}
                  onChange={(event) => setSummary(event.target.value)}
                />
              </div>
            </>
          )}
          <div className="flex flex-wrap gap-2">
            <span className="text-muted-foreground">Tags:</span>
            {bookmark?.tags?.map((tag) => (
              <Badge key={tag.id} variant="secondary">
                {tag.name}
              </Badge>
            ))}
          </div>

          <div className="flex justify-end gap-2">
            <Button className="w-fit" type="submit">
              Save
            </Button>
            <Button
              className="w-fit"
              variant="destructive"
              onClick={(event) => {
                event.preventDefault();
                onDelete();
              }}
            >
              Delete
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
