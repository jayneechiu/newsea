/** Only same-site paths are allowed after login, so `?next=` cannot send users to another origin. */
export function safeNextPath(next: string | null): string {
  return next && next.startsWith("/") && !next.startsWith("//") && !next.startsWith("/\\") ? next : "/";
}

export function loginPath(next: string, mode?: "signup"): string {
  const params = new URLSearchParams({ next });
  if (mode) params.set("mode", mode);
  return `/login?${params}`;
}
