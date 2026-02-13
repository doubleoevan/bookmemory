import { isObject } from "@/utils/object";

export interface ApiError {
  message?: string;
  detail?: string;
  error?: string;
  errors?: { message?: string }[];
}

export function getErrorMessage(error: unknown): string {
  // return the message from a native Error object
  if (error instanceof Error) {
    return error.message || "Something went wrong.";
  }

  // return the message from a possible API error
  if (isObject(error)) {
    const apiError = error as ApiError;
    if (typeof apiError.message === "string") {
      return apiError.message;
    }
    if (typeof apiError.detail === "string") {
      return apiError.detail;
    }
    if (typeof apiError.error === "string") {
      return apiError.error;
    }
    if (
      Array.isArray(apiError.errors) &&
      apiError.errors.length > 0 &&
      typeof apiError.errors[0]?.message === "string"
    ) {
      return apiError.errors[0].message;
    }
  }

  // return the error itself if it's a string'
  if (typeof error === "string") {
    return error;
  }

  // default a default error message
  return "Unexpected error. Please try again.";
}
