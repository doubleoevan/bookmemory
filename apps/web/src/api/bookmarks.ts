import type {
  BookmarkCreateRequest,
  BookmarkPreviewRequest,
  BookmarkPreviewResponse,
  BookmarkResponse,
  BookmarkSearchRequest,
  BookmarkSearchResponse,
  BookmarkUpdateRequest,
  LimitOffsetPageBookmarkResponse,
} from "@bookmemory/contracts";
import {
  createBookmarkApiV1BookmarksPost,
  deleteBookmarkApiV1BookmarksBookmarkIdDelete,
  getBookmarkApiV1BookmarksBookmarkIdGet,
  getBookmarksApiV1BookmarksGet,
  getRelatedBookmarksApiV1BookmarksBookmarkIdRelatedGet,
  loadBookmarkApiV1BookmarksBookmarkIdLoadPost,
  previewBookmarkApiV1BookmarksPreviewPost,
  searchBookmarksApiV1BookmarksSearchPost,
  updateBookmarkApiV1BookmarksBookmarkIdPatch,
} from "@bookmemory/contracts";
import { apiRequest } from "@/api/client";

/**
 * POST /api/v1/bookmarks/preview
 */
export async function previewBookmark(
  body: BookmarkPreviewRequest,
): Promise<BookmarkPreviewResponse> {
  return apiRequest<BookmarkPreviewResponse>(previewBookmarkApiV1BookmarksPreviewPost, {
    body,
  });
}

/**
 * POST /api/v1/bookmarks/
 */
export async function createBookmark(body: BookmarkCreateRequest): Promise<BookmarkResponse> {
  return apiRequest<BookmarkResponse>(createBookmarkApiV1BookmarksPost, {
    body,
  });
}

/**
 * GET /api/v1/bookmarks/
 *
 * Supports query params:
 * - query?: string | null
 * - tag?: string[]
 * - tag_mode?: "any" | "all" | "ignore"
 * - sort?: "alphabetical" | "recent"
 * - limit?: number
 * - offset?: number
 */
export async function getBookmarks(query?: {
  query?: string | null;
  tag?: Array<string>;
  tag_mode?: "any" | "all" | "ignore";
  sort?: "alphabetical" | "recent";
  limit?: number;
  offset?: number;
}): Promise<LimitOffsetPageBookmarkResponse> {
  return apiRequest<LimitOffsetPageBookmarkResponse>(getBookmarksApiV1BookmarksGet, {
    query,
  });
}

/**
 * GET /api/v1/bookmarks/{bookmark_id}
 */
export async function getBookmark(bookmarkId: string): Promise<BookmarkResponse> {
  if (!bookmarkId) {
    throw new Error("bookmarkId is required");
  }

  return apiRequest<BookmarkResponse>(getBookmarkApiV1BookmarksBookmarkIdGet, {
    path: { bookmark_id: bookmarkId },
  });
}

/**
 * PATCH /api/v1/bookmarks/{bookmark_id}
 */
export async function updateBookmark(
  bookmarkId: string,
  body: BookmarkUpdateRequest,
): Promise<BookmarkResponse> {
  if (!bookmarkId) {
    throw new Error("bookmarkId is required");
  }

  return apiRequest<BookmarkResponse>(updateBookmarkApiV1BookmarksBookmarkIdPatch, {
    path: { bookmark_id: bookmarkId },
    body,
  });
}

/**
 * DELETE /api/v1/bookmarks/{bookmark_id}
 */
export async function deleteBookmark(bookmarkId: string): Promise<BookmarkResponse> {
  if (!bookmarkId) {
    throw new Error("bookmarkId is required");
  }

  return apiRequest<BookmarkResponse>(deleteBookmarkApiV1BookmarksBookmarkIdDelete, {
    path: { bookmark_id: bookmarkId },
  });
}

/**
 * POST /api/v1/bookmarks/{bookmark_id}/load
 */
export async function loadBookmark(bookmarkId: string): Promise<BookmarkResponse> {
  if (!bookmarkId) {
    throw new Error("bookmarkId is required");
  }

  return apiRequest<BookmarkResponse>(loadBookmarkApiV1BookmarksBookmarkIdLoadPost, {
    path: { bookmark_id: bookmarkId },
  });
}

/**
 * GET /api/v1/bookmarks/{bookmark_id}/related
 */
export async function getRelatedBookmarks(
  bookmarkId: string,
  query?: {
    tag_mode?: "any" | "all" | "ignore";
    limit?: number;
  },
): Promise<Array<BookmarkSearchResponse>> {
  if (!bookmarkId) {
    throw new Error("bookmarkId is required");
  }

  return apiRequest<Array<BookmarkSearchResponse>>(
    getRelatedBookmarksApiV1BookmarksBookmarkIdRelatedGet,
    {
      path: { bookmark_id: bookmarkId },
      query,
    },
  );
}

/**
 * POST /api/v1/bookmarks/search
 */
export async function searchBookmarks(
  body: BookmarkSearchRequest,
): Promise<Array<BookmarkSearchResponse>> {
  return apiRequest<Array<BookmarkSearchResponse>>(searchBookmarksApiV1BookmarksSearchPost, {
    body,
  });
}
