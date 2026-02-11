import { Button } from "@bookmemory/ui";
import { GoogleLoginIcon } from "@/features/authentication/components/GoogleLoginIcon";
import { useCurrentUser } from "@/features/authentication/hooks/useCurrentUser";
import { Loader } from "@/components/Loader";

export function LoginPage() {
  const { status } = useCurrentUser();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  return (
    <div className="min-h-svh flex flex-col items-center justify-center gap-4">
      {status === "loading" ? (
        <Loader className="w-[10vh] h-[10vh]" />
      ) : (
        <>
          <h1 className="text-3xl">Save bookmarks. Search intelligently.</h1>
          <Button
            onClick={() => {
              window.location.href = `${API_BASE_URL}/api/v1/auth/google/start`;
            }}
            className={`
          flex items-center justify-center
          min-w-1/3
          gap-2 px-6 py-4
          border rounded-md
          bg-primary text-primary-foreground
          font-semibold
        `}
          >
            <GoogleLoginIcon className="w-5 h-5" />
            <span>Continue with Google</span>
          </Button>
        </>
      )}
    </div>
  );
}
