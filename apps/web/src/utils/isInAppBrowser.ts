/**
 * checks if the current browser is an in-app browser that will cause OAuth to fail
 */
export function isInAppBrowser(): boolean {
  if (typeof navigator === "undefined") {
    return false;
  }

  // check for embedded browsers that trigger Google OAuth "disallowed_useragent"
  const userAgent = navigator.userAgent ?? "";
  return (
    /LinkedInApp/i.test(userAgent) ||
    /\bFBAN\b|\bFBAV\b/i.test(userAgent) || // Facebook / Messenger
    /FB_IAB/i.test(userAgent) ||
    /Instagram/i.test(userAgent) ||
    /Snapchat/i.test(userAgent) ||
    /TikTok/i.test(userAgent) ||
    /WhatsApp/i.test(userAgent) ||
    /MicroMessenger/i.test(userAgent) || // WeChat
    /KAKAOTALK/i.test(userAgent) || // KakaoTalk
    /Reddit/i.test(userAgent) ||
    /Line/i.test(userAgent) ||
    /\bwv\b/i.test(userAgent) // Generic Android WebView
  );
}
