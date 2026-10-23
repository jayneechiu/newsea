import apiClient, { hasAccountBackend, syncsToAccount } from "./api";
import {
  clearLocalInteractions,
  readInteractionState,
  writeInteractionState,
  type InteractionState,
  type InteractionType,
} from "./interactions";
import { normalizeTags, type TagId } from "./tags";

const INTEREST_TAGS_KEY = "newsea:interest-tags";

export interface Account {
  id: number;
  email: string;
}

export function readInterestTags(): TagId[] | null {
  const raw = localStorage.getItem(INTEREST_TAGS_KEY);
  if (raw === null) return null;
  try {
    return normalizeTags(JSON.parse(raw) as string[]);
  } catch {
    return [];
  }
}

/** An empty list means "picker skipped", which differs from never having been asked (null). */
export function saveInterestTags(tags: TagId[]) {
  localStorage.setItem(INTEREST_TAGS_KEY, JSON.stringify(tags));
  if (syncsToAccount()) {
    apiClient.put("/me/preferences", { interest_tags: tags }).catch(() => undefined);
  }
}

function rememberSignIn(account: Account) {
  localStorage.setItem("isLoggedIn", "true");
  localStorage.setItem("userEmail", account.email);
}

function forgetSignIn() {
  localStorage.removeItem("isLoggedIn");
  localStorage.removeItem("userEmail");
}

/** Union local (pre-login) data into the account, then mirror the merged result locally. */
async function mergeLocalIntoAccount() {
  const localTags = readInterestTags() ?? [];
  const { interest_tags: serverTags } = (await apiClient.get("/me/preferences")) as unknown as {
    interest_tags: string[];
  };
  if (!serverTags.length && localTags.length) {
    await apiClient.put("/me/preferences", { interest_tags: localTags });
  } else if (serverTags.length) {
    localStorage.setItem(INTEREST_TAGS_KEY, JSON.stringify(normalizeTags(serverTags)));
  }

  const local = readInteractionState();
  const server = (await apiClient.get("/me/interactions")) as unknown as InteractionState;
  const missing = (ids: string[], known: string[], type: InteractionType) =>
    ids.filter((id) => !known.includes(id)).map((id) => ({ card_id: id, type }));
  const events = [
    ...missing(local.liked, server.liked, "like"),
    ...missing(local.saved, server.saved, "save"),
    ...missing(local.hidden, server.hidden, "hide"),
  ];
  const merged = events.length
    ? ((await apiClient.post("/me/interactions", { events })) as unknown as InteractionState)
    : server;
  writeInteractionState(merged);
}

async function signIn(path: "/auth/login" | "/auth/register", email: string, password: string) {
  const account = (await apiClient.post(path, { email, password })) as unknown as Account;
  rememberSignIn(account);
  try {
    await mergeLocalIntoAccount();
  } catch (error) {
    console.warn("Could not merge local preferences into the account yet.", error);
  }
  return account;
}

export const login = (email: string, password: string) => signIn("/auth/login", email, password);
export const register = (email: string, password: string) => signIn("/auth/register", email, password);

export async function logout() {
  if (hasAccountBackend) {
    await apiClient.post("/auth/logout").catch(() => undefined);
    // Keep one account's history from leaking into the next person who signs in on this browser.
    clearLocalInteractions();
    localStorage.removeItem(INTEREST_TAGS_KEY);
  }
  forgetSignIn();
}

/** Re-check the cookie session on load. Returns true when the local sign-in hint changed. */
export async function refreshSession(): Promise<boolean> {
  if (!hasAccountBackend || localStorage.getItem("isLoggedIn") !== "true") return false;
  try {
    rememberSignIn((await apiClient.get("/me")) as unknown as Account);
    return false;
  } catch (error) {
    const status = (error as { response?: { status?: number } }).response?.status;
    if (status !== 401) return false; // backend down: keep the hint rather than signing the user out
    forgetSignIn();
    return true;
  }
}

