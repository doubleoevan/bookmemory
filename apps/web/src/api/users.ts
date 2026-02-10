import { apiRequest } from "@/api/client";
import { type CurrentUser, getAuthenticatedUserApiV1UsersMeGet } from "@bookmemory/contracts";

/**
 * GET /api/v1/users/me
 */
export async function getCurrentUser(): Promise<CurrentUser> {
  return apiRequest<CurrentUser>(getAuthenticatedUserApiV1UsersMeGet);
}
