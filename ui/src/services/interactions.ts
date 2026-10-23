import apiClient, { syncsToAccount } from "./api";

export const SAVED_CARDS_KEY = "newsea:saved-cards";
export const LIKED_CARDS_KEY = "newsea:liked-cards";
export const HIDDEN_CARDS_KEY = "newsea:hidden-cards";
const EVENTS_KEY = "newsea:interaction-events";

export type InteractionType = "like" | "unlike" | "save" | "unsave" | "hide" | "unhide";

interface InteractionEvent {
  cardId: string;
  type: InteractionType;
  at: string;
}

export interface InteractionState {
  liked: string[];
  saved: string[];
  hidden: string[];
}

export function readStoredIds(key: string): string[] {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]") as string[];
  } catch {
    return [];
  }
}

export function setStoredId(key: string, cardId: string, active: boolean) {
  const ids = new Set(readStoredIds(key));
  if (active) ids.add(cardId);
  else ids.delete(cardId);
  localStorage.setItem(key, JSON.stringify([...ids]));
}

export function readInteractionState(): InteractionState {
  return {
    liked: readStoredIds(LIKED_CARDS_KEY),
    saved: readStoredIds(SAVED_CARDS_KEY),
    hidden: readStoredIds(HIDDEN_CARDS_KEY),
  };
}

export function writeInteractionState(state: InteractionState) {
  localStorage.setItem(LIKED_CARDS_KEY, JSON.stringify(state.liked));
  localStorage.setItem(SAVED_CARDS_KEY, JSON.stringify(state.saved));
  localStorage.setItem(HIDDEN_CARDS_KEY, JSON.stringify(state.hidden));
}

export function clearLocalInteractions() {
  [LIKED_CARDS_KEY, SAVED_CARDS_KEY, HIDDEN_CARDS_KEY, EVENTS_KEY].forEach((key) => localStorage.removeItem(key));
}

/** Send events to the signed-in account; local storage stays the source the UI reads from. */
export function pushInteractions(events: Array<{ card_id: string; type: InteractionType }>) {
  if (!syncsToAccount() || !events.length) return;
  apiClient.post("/me/interactions", { events }).catch(() => {
    // Offline or signed out: the local copy is kept and merged again on the next sign-in.
  });
}

export function recordInteraction(cardId: string, type: InteractionType) {
  let events: InteractionEvent[] = [];

  try {
    events = JSON.parse(localStorage.getItem(EVENTS_KEY) || "[]") as InteractionEvent[];
  } catch {
    // A malformed local history should never block the interaction itself.
  }

  const next = [...events, { cardId, type, at: new Date().toISOString() }].slice(-250);
  localStorage.setItem(EVENTS_KEY, JSON.stringify(next));
  pushInteractions([{ card_id: cardId, type }]);
}

export function unhideAllCards() {
  const hidden = readStoredIds(HIDDEN_CARDS_KEY);
  localStorage.removeItem(HIDDEN_CARDS_KEY);
  pushInteractions(hidden.map((cardId) => ({ card_id: cardId, type: "unhide" as const })));
}
