import { Link } from "react-router-dom";
import { cn } from "@bookmemory/ui";
import UserMenu from "@/components/UserMenu";
import { HeaderIcon } from "@/components/HeaderIcon";

export function Header({ className }: { className?: string }) {
  return (
    <header className={cn("bg-background", className)}>
      <nav
        className="mx-auto flex h-14 items-center justify-between px-4 pr-2 bg-background"
        aria-label="Primary navigation"
      >
        {/* logo */}
        <Link
          to="/"
          className="
            flex items-center gap-2
            font-semibold text-primary
            hover:opacity-90
          "
          aria-label="Go to Bookmarks Home"
        >
          <HeaderIcon />
          <span>BookMemory</span>
        </Link>

        {/* tagline */}
        <span className="hidden sm:inline! text-sm text-muted-foreground">
          A search engine for bookmarks. <span className="inline-block text-base">🧠✨</span>
        </span>

        {/* user menu */}
        <UserMenu />
      </nav>
    </header>
  );
}
