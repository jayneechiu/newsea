import assert from "node:assert/strict";
import { test } from "node:test";
import type { ContentCard } from "../types/content.ts";
import { EXPLORE_EVERY, rankForYou } from "./ranking.ts";

function card(id: string, topics: string[]): ContentCard {
  return {
    id,
    lane: ["everyone"],
    cardType: "trend",
    theme: "ink",
    eyebrow: "",
    headline: id,
    context: "",
    takeaways: [],
    topics,
    audience: "",
    sourceCount: 1,
    communityCount: 1,
    trendLabel: "",
    sources: [],
  };
}

const noSignals = { tags: [], likedIds: [], savedIds: [], hiddenIds: [] };

test("cards matching chosen tags come first", () => {
  const cards = [card("dev", ["software"]), card("bbq", ["food"]), card("cash", ["money"])];
  const ranked = rankForYou(cards, { ...noSignals, tags: ["food"] }, "2026-01-01");
  assert.equal(ranked[0].id, "bbq");
});

test("hidden cards are removed and duplicates collapsed", () => {
  const cards = [card("a", ["food"]), card("b", ["money"]), card("a", ["food"])];
  const ranked = rankForYou(cards, { ...noSignals, hiddenIds: ["b"] }, "seed");
  assert.deepEqual(ranked.map((c) => c.id), ["a"]);
});

test("liked and saved topics boost related cards", () => {
  const cards = [card("liked", ["travel"]), card("related", ["travel"]), card("other", ["money"])];
  const ranked = rankForYou(cards, { ...noSignals, likedIds: ["liked"] }, "seed");
  assert.deepEqual(ranked.slice(0, 2).map((c) => c.id).sort(), ["liked", "related"]);
});

test("roughly every fifth slot is an exploration card", () => {
  const matched = Array.from({ length: 12 }, (_, i) => card(`food-${i}`, ["food"]));
  const unmatched = Array.from({ length: 6 }, (_, i) => card(`misc-${i}`, ["books"]));
  const ranked = rankForYou([...matched, ...unmatched], { ...noSignals, tags: ["food"] }, "seed");
  ranked.forEach((c, index) => {
    const isExploreSlot = (index + 1) % EXPLORE_EVERY === 0;
    if (index < 15) assert.equal(c.id.startsWith("misc"), isExploreSlot, `slot ${index}: ${c.id}`);
  });
  assert.equal(ranked.length, 18);
});

test("the same seed gives the same order", () => {
  const cards = Array.from({ length: 10 }, (_, i) => card(`c${i}`, ["misc"]));
  assert.deepEqual(rankForYou(cards, noSignals, "day-1"), rankForYou(cards, noSignals, "day-1"));
});
