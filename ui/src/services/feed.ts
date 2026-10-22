import apiClient from "./api";
import demoCardsJson from "@/data/demo-cards.json";
import demoRefreshCardsJson from "@/data/demo-refresh-cards.json";
import type { ContentCard, FeedLane, LiveSnapshot } from "@/types/content";

const demoCards = demoCardsJson as ContentCard[];
// Extra preview cards revealed by the refresh button so the demo feels live.
const demoRefreshCards = demoRefreshCardsJson as ContentCard[];
const allDemoCards = [...demoCards, ...demoRefreshCards];
const REFRESH_BATCH_SIZE = 3;
const CARD_CACHE_KEY = "newsea:feed-card-cache";

export interface FeedResult {
  cards: ContentCard[];
  source: "api" | "mock" | "fallback" | "live";
}

let liveSnapshot: Promise<LiveSnapshot | null> | undefined;

/** Static Reddit snapshot refreshed by .github/workflows/live-snapshot.yml; null when not deployed. */
export function getLiveSnapshot(): Promise<LiveSnapshot | null> {
  liveSnapshot ??= fetch(`${import.meta.env.BASE_URL}live/live-cards.json`)
    .then((response) => (response.ok ? (response.json() as Promise<LiveSnapshot>) : null))
    .then((snapshot) => (snapshot?.cards?.length ? snapshot : null))
    .catch(() => null);
  return liveSnapshot;
}

const cardsForLane = (lane: FeedLane, refreshRound = 0) => {
  const inLane = (card: ContentCard) => card.lane.includes(lane);
  const revealed = demoRefreshCards
    .filter(inLane)
    .slice(0, refreshRound * REFRESH_BATCH_SIZE)
    .reverse();
  return [...revealed, ...demoCards.filter(inLane)];
};

function readCachedCards(): ContentCard[] {
  try {
    return JSON.parse(sessionStorage.getItem(CARD_CACHE_KEY) || "[]") as ContentCard[];
  } catch {
    return [];
  }
}

function cacheCards(cards: ContentCard[]) {
  const byId = new Map(readCachedCards().map((card) => [card.id, card]));
  cards.forEach((card) => byId.set(card.id, card));
  sessionStorage.setItem(CARD_CACHE_KEY, JSON.stringify([...byId.values()]));
}

export function getContentCardById(cardId: string): ContentCard | undefined {
  return allDemoCards.find((card) => card.id === cardId) ??
    readCachedCards().find((card) => card.id === cardId);
}

export function getRelatedContentCards(card: ContentCard, limit = 4): ContentCard[] {
  return allDemoCards
    .filter((candidate) => candidate.id !== card.id)
    .map((candidate) => ({
      candidate,
      sharedTopics: candidate.topics.filter((topic) => card.topics.includes(topic)).length,
    }))
    .filter(({ sharedTopics }) => sharedTopics > 0)
    .sort((a, b) => b.sharedTopics - a.sharedTopics)
    .slice(0, limit)
    .map(({ candidate }) => candidate);
}

export async function getContentFeed(lane: FeedLane, refreshRound = 0): Promise<FeedResult> {
  if (lane === "live") {
    const cards = (await getLiveSnapshot())?.cards ?? [];
    cacheCards(cards);
    return { cards, source: "live" };
  }

  if (import.meta.env.VITE_USE_MOCK_DATA === "true") {
    const cards = cardsForLane(lane, refreshRound);
    cacheCards(cards);
    return { cards, source: "mock" };
  }

  try {
    const response = (await apiClient.get("/feed", {
      params: { lane, limit: 40 },
    })) as unknown as { cards: ContentCard[] };

    if (!response.cards?.length) {
      throw new Error("The feed API returned no cards");
    }

    cacheCards(response.cards);
    return { cards: response.cards, source: "api" };
  } catch (error) {
    console.warn("Feed API unavailable; using local fallback cards.", error);
    const cards = cardsForLane(lane, refreshRound);
    cacheCards(cards);
    return { cards, source: "fallback" };
  }
}
