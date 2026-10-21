export const SAVED_CARDS_KEY = "newsea:saved-cards";
export const LIKED_CARDS_KEY = "newsea:liked-cards";
export const HIDDEN_CARDS_KEY = "newsea:hidden-cards";

type InteractionType = "like" | "unlike" | "save" | "unsave" | "hide";

interface InteractionEvent {
  cardId: string;
  type: InteractionType;
  at: string;
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

export function recordInteraction(cardId: string, type: InteractionType) {
  const key = "newsea:interaction-events";
  let events: InteractionEvent[] = [];

  try {
    events = JSON.parse(localStorage.getItem(key) || "[]") as InteractionEvent[];
  } catch {
    // A malformed local history should never block the interaction itself.
  }

  const next = [...events, { cardId, type, at: new Date().toISOString() }].slice(-250);
  localStorage.setItem(key, JSON.stringify(next));
}
