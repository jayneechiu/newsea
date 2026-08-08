import apiClient from "./api";
import demoCardsJson from "@/data/demo-cards.json";
import type { ContentCard, FeedLane } from "@/types/content";

const demoCards = demoCardsJson as ContentCard[];

export interface FeedResult {
  cards: ContentCard[];
  source: "api" | "mock" | "fallback";
}

const cardsForLane = (lane: FeedLane) =>
  demoCards.filter((card) => card.lane.includes(lane));

export async function getContentFeed(lane: FeedLane): Promise<FeedResult> {
  if (import.meta.env.VITE_USE_MOCK_DATA === "true") {
    return { cards: cardsForLane(lane), source: "mock" };
  }

  try {
    const response = (await apiClient.get("/feed", {
      params: { lane, limit: 40 },
    })) as unknown as { cards: ContentCard[] };

    if (!response.cards?.length) {
      throw new Error("The feed API returned no cards");
    }

    return { cards: response.cards, source: "api" };
  } catch (error) {
    console.warn("Feed API unavailable; using local fallback cards.", error);
    return { cards: cardsForLane(lane), source: "fallback" };
  }
}
