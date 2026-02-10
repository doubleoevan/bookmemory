import { useEffect, useState } from "react";
import type { CurrentUser } from "@bookmemory/contracts";
import { getCurrentUser } from "@/api";

type CurrentUserState =
  | { status: "loading"; user?: undefined; message?: undefined }
  | { status: "signed_out"; user?: undefined; message?: undefined }
  | { status: "error"; user?: undefined; message: string }
  | { status: "signed_in"; user: CurrentUser; message?: undefined };

export function useCurrentUser(): CurrentUserState {
  const [state, setState] = useState<CurrentUserState>({ status: "loading" });

  useEffect(() => {
    let isMounted = true;

    async function loadCurrentUser(): Promise<void> {
      try {
        const user = await getCurrentUser();
        if (!isMounted) {
          return;
        }

        setState({ status: "signed_in", user });
      } catch (error) {
        if (!isMounted) {
          return;
        }

        if (error instanceof Response && error.status === 401) {
          setState({ status: "signed_out" });
          return;
        }

        if (error instanceof Response) {
          setState({ status: "error", message: `Request failed: ${error.status}` });
          return;
        }

        setState({ status: "error", message: "Network error" });
      }
    }

    void loadCurrentUser();
    return () => {
      isMounted = false;
    };
  }, []);

  return state;
}
