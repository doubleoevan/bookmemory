import { useEffect, useState } from "react";
import type { paths } from "@bookmemory/contracts";
import { httpRequest } from "@/api/client";

type CurrentUserResponse =
  paths["/api/v1/users/me"]["get"]["responses"]["200"]["content"]["application/json"];

type CurrentUserState =
  | { status: "loading" }
  | { status: "signed_out" }
  | { status: "error"; message: string }
  | { status: "signed_in"; user: CurrentUserResponse };

export function useCurrentUser(): CurrentUserState & {
  user?: CurrentUserResponse;
  message?: string;
} {
  const [userState, setUserState] = useState<CurrentUserState>({ status: "loading" });

  // load the current user when on mount
  useEffect(() => {
    let isMounted = true; // a flag to prevent updating state if the component unmounts

    // load the current user and set the user state
    async function loadCurrentUser(): Promise<void> {
      try {
        const response = await httpRequest("/api/v1/users/me");
        if (!isMounted) {
          return;
        }

        if (response.status === 401) {
          setUserState({ status: "signed_out" });
          return;
        }

        if (!response.ok) {
          setUserState({ status: "error", message: `Request failed: ${response.status}` });
          return;
        }

        const user = (await response.json()) as CurrentUserResponse;
        setUserState({ status: "signed_in", user });
      } catch {
        // ignore if unmounted
        if (!isMounted) {
          return;
        }

        // set the network error state
        setUserState({
          status: "error",
          message: "Network error",
        });
      }
    }
    void loadCurrentUser();

    // cancel a request when the component unmounts
    return () => {
      isMounted = false;
    };
  }, []);

  return userState;
}
