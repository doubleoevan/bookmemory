// apps/web/src/api/summary.ts
import ndjsonStream from "can-ndjson-stream";

type StreamEvent =
  | { chunk: string }
  | { done: true }
  | { error: { code: string; message: string } }
  | Record<string, unknown>;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isAbortError(error: unknown) {
  return error instanceof Error && error.name === "AbortError";
}

function isErrorEvent(event: unknown): event is { error: { code: string; message: string } } {
  if (!isRecord(event)) {
    return false;
  }
  if (!("error" in event)) {
    return false;
  }
  if (!isRecord(event.error)) {
    return false;
  }
  return typeof event.error.code === "string" && typeof event.error.message === "string";
}

function isChunkEvent(event: unknown): event is { chunk: string } {
  if (!isRecord(event)) {
    return false;
  }
  return "chunk" in event && typeof event.chunk === "string";
}

function isDoneEvent(event: unknown): event is { done: true } {
  if (!isRecord(event)) {
    return false;
  }
  return "done" in event && event.done === true;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();
function toApiUrl(url: string): string {
  // already absolute (or data:, blob:, etc.) — leave it
  const isAbsoluteUrl = /^https?:\/\//i.test(url);
  if (isAbsoluteUrl) {
    return url;
  }

  // no base configured — keep relative (dev proxy / same-origin)
  if (!API_BASE_URL) {
    return url;
  }

  // join without double slashes
  const baseUrl = API_BASE_URL.replace(/\/$/, "");
  const path = url.startsWith("/") ? url : `/${url}`;
  return `${baseUrl}${path}`;
}

/**
 * POST /api/v1/bookmarks/{bookmark_id}/summary (stream)
 */
export async function streamSummary(
  bookmarkId: string,
  request: RequestInit = {},
  {
    signal,
    onChunk,
    onComplete,
    onError,
    onEventError,
  }: {
    signal?: AbortSignal;
    onChunk: (chunk: string) => void;
    onComplete: () => void;
    onError: (error: { code: string; message: string }) => void;
    onEventError?: (error: { code: string; message: string }) => void;
  },
) {
  // fetch the response
  let response: Response;
  try {
    const url = toApiUrl(`/api/v1/bookmarks/${bookmarkId}/summary`);
    response = await fetch(url, {
      ...request,
      method: request.method ?? "POST",
      credentials: "include",
      headers: new Headers({
        accept: "application/x-ndjson",
        ...(request.headers ?? {}),
      }),
      signal: signal ?? request.signal,
    });
  } catch (error) {
    if (isAbortError(error)) {
      return;
    }
    onError({
      code: "INTERNAL",
      message: error instanceof Error ? error.message : "Network error",
    });
    return;
  }

  // handle http errors
  if (!response.ok) {
    onError({
      code: "HTTP_ERROR",
      message: `Failed to stream summary (${response.status})`,
    });
    return;
  }

  // check if the response has a body before streaming it
  if (!response.body) {
    onError({ code: "INTERNAL", message: "Missing response body" });
    return;
  }

  // stream the response as ndjson
  const reader = ndjsonStream(response.body).getReader();
  try {
    while (true) {
      // exit the loop when the reader is done
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      // trigger an error event handler
      const event = value as StreamEvent;
      if (isErrorEvent(event)) {
        if (onEventError) {
          onEventError(event.error);
          continue;
        }
        onError(event.error);
        return;
      }

      // trigger a chunk event handler
      if (isChunkEvent(event)) {
        onChunk(event.chunk);
        continue;
      }

      // trigger a done event handler
      if (isDoneEvent(event)) {
        onComplete();
        return;
      }
    }

    onComplete();
  } catch (error) {
    if (isAbortError(error)) {
      return;
    }
    onError({
      code: "INTERNAL",
      message: error instanceof Error ? error.message : "Streaming error",
    });
  } finally {
    try {
      await reader.cancel();
      reader.releaseLock();
    } catch {
      // ignore
    }
  }
}
