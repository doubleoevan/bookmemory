import { Link } from "react-router-dom";
import UserMenu from "@/components/UserMenu";
import { BookMemoryIcon } from "@/components/BookMemoryIcon";

export function Header() {
  return (
    <header className="border-b">
      <nav
        className="mx-auto flex h-14 items-center justify-between px-4 pr-2"
        aria-label="Primary navigation"
      >
        {/* logo */}
        <Link
          to="/"
          className="flex items-center gap-2 font-semibold hover:opacity-90"
          aria-label="Go to Bookmarks Home"
        >
          <BookMemoryIcon />
          <span>BookMemory</span>
        </Link>

        {/* tagline */}
        <span className="text-sm">
          A search engine for bookmarks. <span className="inline-block text-base">🧠✨</span>
        </span>

        {/* user menu */}
        <UserMenu />
      </nav>
    </header>
  );
}
