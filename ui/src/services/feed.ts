import apiClient from "./api";
import demoCardsJson from "@/data/demo-cards.json";
import type { ContentCard, FeedLane } from "@/types/content";

const demoCards = demoCardsJson as ContentCard[];
const CARD_CACHE_KEY = "newsea:feed-card-cache";

export interface FeedResult {
  cards: ContentCard[];
  source: "api" | "mock" | "fallback";
}

const cardsForLane = (lane: FeedLane) =>
  demoCards.filter((card) => card.lane.includes(lane));

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
  return demoCards.find((card) => card.id === cardId) ??
    readCachedCards().find((card) => card.id === cardId);
}

export function getRelatedContentCards(card: ContentCard, limit = 4): ContentCard[] {
  return demoCards
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

export async function getContentFeed(lane: FeedLane): Promise<FeedResult> {
  if (import.meta.env.VITE_USE_MOCK_DATA === "true") {
    const cards = cardsForLane(lane);
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
    const cards = cardsForLane(lane);
    cacheCards(cards);
    return { cards, source: "fallback" };
  }
}
