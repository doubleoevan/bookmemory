import { useState } from "react";
import { BookmarkSearch } from "@/features/bookmarks/components/BookmarkSearch";
import { BookmarkList } from "@/features/bookmarks/components/BookmarkList";
import { AddBookmarkModal } from "@/features/bookmarks/components/AddBookmarkModal";
import { EditBookmarkModal } from "@/features/bookmarks/components/EditBookmarkModal";
import { ViewBookmarkModal } from "@/features/bookmarks/components/ViewBookmarkModal";
import { SummaryProvider } from "@/features/bookmarks/providers/summary";
import { RemoveBookmarkModal } from "@/features/bookmarks/components/RemoveBookmarkModal";

type ModalType = "addBookmark" | "editBookmark" | "viewBookmark" | "deleteBookmark";

export function BookmarksHomePage() {
  const [modalType, setModalType] = useState<ModalType | null>(null);
  const onCloseModal = () => setModalType(null);

  const openAddBookmarkModal = () => setModalType("addBookmark");
  const openEditBookmarkModal = () => setModalType("editBookmark");
  const openViewBookmarkModal = () => setModalType("viewBookmark");
  const openDeleteBookmarkModal = () => setModalType("deleteBookmark");

  return (
    <div className="mx-auto w-full max-w-4xl p-4">
      <BookmarkSearch onAddBookmarkClick={openAddBookmarkModal} />
      <BookmarkList
        onAddBookmarkClick={openAddBookmarkModal}
        onBookmarkClick={openViewBookmarkModal}
      />

      {/* Bookmark Modals */}
      <SummaryProvider>
        {modalType === "addBookmark" ? (
          <AddBookmarkModal onClose={onCloseModal} onEdit={openEditBookmarkModal} />
        ) : modalType === "editBookmark" ? (
          <EditBookmarkModal
            onClose={onCloseModal}
            onView={openViewBookmarkModal}
            onDelete={openDeleteBookmarkModal}
          />
        ) : modalType === "viewBookmark" ? (
          <ViewBookmarkModal onClose={onCloseModal} onEdit={openEditBookmarkModal} />
        ) : modalType === "deleteBookmark" ? (
          <RemoveBookmarkModal onClose={onCloseModal} onEdit={openEditBookmarkModal} />
        ) : null}
      </SummaryProvider>
    </div>
  );
}
