import { Button, toast } from "@bookmemory/ui";
import { GoogleLoginIcon } from "@/features/authentication/components/GoogleLoginIcon";
import { useCurrentUser } from "@/features/authentication/hooks/useCurrentUser";
import { Loader } from "@/components/Loader";
import { useTheme } from "@/app/theme";
import { isInAppBrowser } from "@/utils/isInAppBrowser";

export function LoginPage() {
  const { status } = useCurrentUser();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const inAppBrowser = isInAppBrowser(); // try to open an in-app browser in an external browser if necessary

  // open the Google login page
  const onGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/api/v1/auth/google/start`;
  };

  // copy the url to the clipboard
  const onClipboardCopy = async () => {
    if (typeof window === "undefined") {
      return;
    }

    // try navigator.clipboard to copy paste
    const url = window.location.href;
    try {
      if (navigator.clipboard?.writeText == null) {
        throw new Error("clipboard not available");
      }
      await navigator.clipboard.writeText(url);
      toast.success("Link copied to clipboard");
      return;
    } catch {
      // fall through to legacy copy paste if navigator.clipboard is not available
    }

    // fallback to creating a textarea and selecting its contents
    let textarea: HTMLTextAreaElement | null = null;
    try {
      textarea = document.createElement("textarea");
      textarea.value = url;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      textarea.setSelectionRange(0, textarea.value.length);
      document.execCommand("copy");
      toast.success("Link copied to clipboard");
    } catch {
      toast.error("Unable to copy link");
    } finally {
      textarea?.remove();
    }
  };

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
        <Loader className="w-[10vw] h-[10dvh]" />
      ) : inAppBrowser ? (
        <section aria-labelledby="page-heading" className="w-full max-w-xl text-center">
          {/* prompts to open in an external browser */}
          <header className="text-center">
            <h1 id="page-heading" className="text-3xl sm:text-4xl pb-4">
              Open in Chrome or Safari
            </h1>
          </header>

          {/* open in browser button */}
          <div className="flex flex-col gap-3 items-center">
            <a
              href={typeof window !== "undefined" ? window.location.href : "https://bookmemory.io"}
              target="_blank"
              rel="noopener noreferrer"
              className="
                flex items-center justify-center
                w-full
                mx-auto gap-2
                p-4
                border rounded-lg
                bg-primary text-primary-foreground
                font-semibold
              "
            >
              Open in Browser
            </a>

            {/* open in browser instructions */}
            <p className="text-sm text-muted-foreground">
              If that button doesn’t work, tap the app’s <span aria-hidden="true">•••</span> menu
              and choose <span className="font-medium">Open in Browser</span>.
            </p>

            {/* url to copy and paste and open in a browser */}
            <div className="w-full pt-2 text-center flex flex-col items-center">
              <div className="text-xs text-muted-foreground pb-2">Or click to copy this link:</div>

              <button
                type="button"
                onClick={onClipboardCopy}
                className="
                  w-fit
                  break-all rounded-md border p-3
                  bg-accent hover:bg-accent/80
                  cursor-pointer
                  text-left
                "
              >
                {typeof window !== "undefined" ? window.location.href : "https://bookmemory.io"}
              </button>
            </div>
          </div>
        </section>
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
            onClick={onGoogleLogin}
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
