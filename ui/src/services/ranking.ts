import type { ContentCard } from "../types/content.ts";
import { tagsForCard } from "./tags.ts";

export interface RankingSignals {
  tags: string[];
  likedIds: string[];
  savedIds: string[];
  hiddenIds: string[];
}

/** Every Nth slot is filled with an unmatched card so the feed keeps ~20% exploration. */
export const EXPLORE_EVERY = 5;

const TAG_WEIGHT = 3;
const LIKE_WEIGHT = 1;
const SAVE_WEIGHT = 1.5;
const HIDE_WEIGHT = -0.5;

function hashString(value: string): number {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

/** Stable pseudo-random value in [0, 1) per (seed, id), so a day's order doesn't jump around. */
function jitter(seed: string, id: string): number {
  return hashString(`${seed}:${id}`) / 2 ** 32;
}

export function rankForYou(cards: ContentCard[], signals: RankingSignals, seed: string): ContentCard[] {
  const byId = new Map<string, ContentCard>();
  cards.forEach((card) => byId.set(card.id, card));
  const pool = [...byId.values()];

  const hidden = new Set(signals.hiddenIds);
  const chosenTags = new Set(signals.tags);
  const topicWeights = new Map<string, number>();
  const addTopics = (ids: string[], weight: number) =>
    ids.forEach((id) =>
      byId.get(id)?.topics.forEach((topic) => topicWeights.set(topic, (topicWeights.get(topic) ?? 0) + weight)),
    );
  addTopics(signals.likedIds, LIKE_WEIGHT);
  addTopics(signals.savedIds, SAVE_WEIGHT);
  addTopics(signals.hiddenIds, HIDE_WEIGHT);

  const scored = pool
    .filter((card) => !hidden.has(card.id))
    .map((card) => {
      const tagScore = tagsForCard(card).filter((tag) => chosenTags.has(tag)).length * TAG_WEIGHT;
      const topicScore = card.topics.reduce((sum, topic) => sum + (topicWeights.get(topic) ?? 0), 0);
      return { card, score: tagScore + topicScore, tieBreak: jitter(seed, card.id) };
    });

  const byScore = (a: (typeof scored)[number], b: (typeof scored)[number]) =>
    b.score - a.score || a.tieBreak - b.tieBreak;
  const matched = scored.filter((item) => item.score > 0).sort(byScore);
  const explore = scored.filter((item) => item.score <= 0).sort(byScore);

  const ranked: ContentCard[] = [];
  while (matched.length || explore.length) {
    const exploreSlot = (ranked.length + 1) % EXPLORE_EVERY === 0;
    const next = (exploreSlot ? explore.shift() ?? matched.shift() : matched.shift() ?? explore.shift())!;
    ranked.push(next.card);
  }
  return ranked;
}

export function dailySeed(date = new Date()): string {
  return date.toISOString().slice(0, 10);
}
