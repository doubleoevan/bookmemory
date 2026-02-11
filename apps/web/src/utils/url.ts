export function getDomain(url: string) {
  return new URL(url).hostname.replace("www.", "");
}
