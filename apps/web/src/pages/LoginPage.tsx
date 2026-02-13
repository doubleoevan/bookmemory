import { Button } from "@bookmemory/ui";
import { GoogleLoginIcon } from "@/features/authentication/components/GoogleLoginIcon";
import { useCurrentUser } from "@/features/authentication/hooks/useCurrentUser";
import { Loader } from "@/components/Loader";
import { useTheme } from "@/app/theme";

export function LoginPage() {
  const { status } = useCurrentUser();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  return (
    <main
      className="
        min-h-svh
        flex flex-col items-center justify-center
        mx-auto max-w-4xl
        p-4
      "
    >
      {status === "loading" ? (
        <Loader className="w-[10vh] h-[10vh]" />
      ) : (
        <section aria-labelledby="page-heading">
          <header className="text-center">
            <h1 id="page-heading" className="text-4xl pb-8">
              Save bookmarks. Search intelligently.
            </h1>
          </header>

          <section className="flex items-center gap-4 pb-8">
            <h2 className="sr-only">Product Features</h2>
            <figure className="text-center">
              <figcaption className="p-4">Summarize and find related bookmarks with AI</figcaption>
              <img
                src={
                  isDark ? "/screenshots/ai_summary_light.png" : "/screenshots/ai_summary_dark.png"
                }
                alt="Bookmark detail view showing an AI-generated summary, extracted description, tags, and related bookmarks powered by semantic search."
                className="rounded-xl"
                loading="lazy"
              />
            </figure>
            <figure className="text-center">
              <figcaption className="p-4">Search for bookmarks semantically by meaning</figcaption>
              <img
                src={
                  isDark
                    ? "/screenshots/vector_search_light.png"
                    : "/screenshots/vector_search_dark.png"
                }
                alt="Search results page showing semantic search for 'vector' with highlighted matches and tag filters."
                className="rounded-xl"
                loading="lazy"
              />
            </figure>
          </section>

          <Button
            onClick={() => {
              window.location.href = `${API_BASE_URL}/api/v1/auth/google/start`;
            }}
            className="
              flex items-center justify-center
              min-w-1/3
              mx-auto gap-2
              p-6
              border rounded-lg
              bg-primary text-primary-foreground
              font-semibold
            "
          >
            <GoogleLoginIcon className="w-5 h-5" aria-hidden="true" focusable="false" />
            <span>Continue with Google</span>
          </Button>
        </section>
      )}
    </main>
  );
}
