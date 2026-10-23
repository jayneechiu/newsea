import apiClient from "./api";
import demoCardsJson from "@/data/demo-cards.json";
import demoRefreshCardsJson from "@/data/demo-refresh-cards.json";
import type { ContentCard, FeedLane, LiveSnapshot } from "@/types/content";
import { readInterestTags } from "./account";
import { readInteractionState } from "./interactions";
import { dailySeed, rankForYou } from "./ranking";
import { tagsForCard, type TagId } from "./tags";

const demoCards = demoCardsJson as ContentCard[];
// Extra preview cards revealed by the refresh button so the demo feels live.
const demoRefreshCards = demoRefreshCardsJson as ContentCard[];
const allDemoCards = [...demoCards, ...demoRefreshCards];
const REFRESH_BATCH_SIZE = 3;
const CARD_CACHE_KEY = "newsea:feed-card-cache";

export interface FeedResult {
  cards: ContentCard[];
  source: "api" | "mock" | "fallback";
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

const cardsForLane = (lane: FeedLane | null, refreshRound = 0) => {
  const inLane = (card: ContentCard) => lane === null || card.lane.includes(lane);
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

/** Home tabs: "hot" mixes every card (preview + live); a tag tab narrows it to that interest or place. */
export type FeedTab = "hot" | TagId;

const NO_SIGNALS = { tags: [], likedIds: [], savedIds: [], hiddenIds: [] };

/** Signed-in readers get their personal ranking (interests, likes, saves, hides); guests get one shared daily order. */
export async function getHomeFeed(tab: FeedTab, refreshRound: number, personalized: boolean): Promise<FeedResult> {
  const base = await getContentFeed("everyone", refreshRound);
  // Preview data: widen to every lane's cards; API data: the API already returns the broad feed.
  const pool = base.source === "api" ? base.cards : cardsForLane(null, refreshRound);
  const liveCards = (await getLiveSnapshot())?.cards ?? [];
  const { liked, saved, hidden } = readInteractionState();
  const signals = personalized
    ? { tags: readInterestTags() ?? [], likedIds: liked, savedIds: saved, hiddenIds: hidden }
    : NO_SIGNALS;
  const cards = rankForYou([...pool, ...liveCards], signals, dailySeed()).filter(
    (card) => tab === "hot" || tagsForCard(card).includes(tab),
  );
  cacheCards(cards);
  return { cards, source: base.source };
}

/** Cards bundled with the app for previews; everything else came from Reddit. */
export function isDemoCard(card: ContentCard): boolean {
  return allDemoCards.some((demo) => demo.id === card.id);
}

export async function getContentFeed(lane: FeedLane, refreshRound = 0): Promise<FeedResult> {
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
