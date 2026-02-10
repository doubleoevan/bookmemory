import { getTagsApiV1TagsGet, type TagCountResponse } from "@bookmemory/contracts";
import { apiRequest } from "@/api/client";

/**
 * GET /api/v1/tags
 */
export async function getTags(): Promise<Array<TagCountResponse>> {
  return apiRequest<Array<TagCountResponse>>(getTagsApiV1TagsGet);
}
