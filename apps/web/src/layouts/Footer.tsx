import { ExternalLink } from "@/components/ExternalLink";

const REPO_URL = "https://github.com/doubleoevan/bookmemory";

export function Footer() {
  return (
    <footer className="border-t">
      <div className="mx-auto max-w-7xl px-4 py-6 text-center text-sm text-muted-foreground">
        <p>BookMemory is a selfish project for the author’s own personal growth.</p>
        <p>It uses semantic vector embeddings to search by meaning instead of keywords.</p>
        <p>
          The code can be found <ExternalLink href={REPO_URL}>here</ExternalLink>.
        </p>
      </div>
    </footer>
  );
}
