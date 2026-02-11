interface BookmarkSearchProps {
  onAddBookmarkClick?: () => void;
}

export function BookmarkSearch({ onAddBookmarkClick }: BookmarkSearchProps) {
  console.log(onAddBookmarkClick);
  return <div>BookmarkSearch</div>;
}
