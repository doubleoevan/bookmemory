export function getDomain(url: string) {
  return new URL(url).hostname.replace("www.", "");
}

export function normalizeUrl(input: string): string {
  // ignore an empty url
  const trimmed_url = input.trim();
  if (!trimmed_url) {
    return trimmed_url;
  }

  // prepend https if http is missing
  const hasHttp = /^https?:\/\//i.test(trimmed_url);
  if (hasHttp) {
    return trimmed_url;
  }
  return `https://${trimmed_url}`;
}

export function isUrlValid(url: string): boolean {
  // verify the url is not empty
  const trimmedUrl = url.trim();
  if (!trimmedUrl) {
    return false;
  }

  // verify protocol is present
  try {
    const parsed = new URL(trimmedUrl);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}
