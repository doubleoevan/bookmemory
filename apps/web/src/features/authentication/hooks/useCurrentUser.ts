import { useEffect, useState } from "react";
import type { CurrentUser } from "@bookmemory/contracts";
import { getCurrentUser } from "@/api";
import { getErrorMessage } from "@/utils/error";

type CurrentUserState =
  | { status: "loading"; user?: undefined; message?: undefined }
  | { status: "signed_out"; user?: undefined; message?: undefined }
  | { status: "error"; user?: undefined; message: string }
  | { status: "signed_in"; user: CurrentUser; message?: undefined };

export function useCurrentUser(): CurrentUserState {
  const [userState, setUserState] = useState<CurrentUserState>({ status: "loading" });

  useEffect(() => {
    let isMounted = true;

    async function loadCurrentUser(): Promise<void> {
      try {
        const user = await getCurrentUser();
        if (!isMounted) {
          return;
        }

        setUserState({ status: "signed_in", user });
      } catch (error) {
        if (!isMounted) {
          return;
        }

        const errorMessage = getErrorMessage(error);
        if (
          errorMessage === "Not authenticated" ||
          errorMessage === "Invalid token" ||
          errorMessage === "Expired token" ||
          errorMessage === "Invalid refresh token" ||
          errorMessage === "Refresh token expired"
        ) {
          setUserState({ status: "signed_out" });
          return;
        }

        if (error instanceof Response) {
          setUserState({ status: "error", message: `Request failed: ${error.status}` });
          return;
        }

        setUserState({ status: "error", message: "Network error" });
      }
    }

    void loadCurrentUser();
    return () => {
      isMounted = false;
    };
  }, []);

  return userState;
}
