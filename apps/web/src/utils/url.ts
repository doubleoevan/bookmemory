import isUrlHttp from "is-url-http";

export function getDomain(url: string) {
  return new URL(url).hostname.replace("www.", "");
}

export function normalizeUrl(input: string): string {
  // ignore an empty url
  const url = input.trim();
  if (!url) {
    return url;
  }

  // prepend https if http is missing
  const hasHttp = /^https?:\/\//i.test(url);
  if (hasHttp) {
    return url;
  }
  return `https://${url}`;
}

export function isUrlValid(url: string): boolean {
  return isUrlHttp(url.trim());
}
