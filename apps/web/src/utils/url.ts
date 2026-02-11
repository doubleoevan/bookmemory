export function getDomain(url: string) {
  return new URL(url).hostname.replace("www.", "");
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
