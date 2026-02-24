import { ExternalLink } from "@/components/ExternalLink";

const REPO_URL = "https://github.com/doubleoevan/bookmemory";

export function Footer({ className }: { className?: string }) {
  return (
    <footer className={className}>
      <div className="mx-auto max-w-7xl px-4 py-6 text-center text-sm text-muted-foreground bg-background">
        <p>BookMemory is a selfish project for the author’s own personal growth.</p>
        <p>It uses semantic vector embeddings to search by meaning as well as keyword.</p>
        <p>
          <span>The code can be found </span>
          <ExternalLink className="text-primary font-semibold dark:text-primary/70" href={REPO_URL}>
            here
          </ExternalLink>
          .
        </p>
      </div>
    </footer>
  );
}
