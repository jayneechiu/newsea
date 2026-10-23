import assert from "node:assert/strict";
import { test } from "node:test";
import { cardSubreddits, isTagId, normalizeTags, tagsForCard, tagsForSubreddits } from "./tags.ts";

test("mock cards map to tags through their topics", () => {
  assert.deepEqual(tagsForCard({ topics: ["food", "local", "dallas"], eyebrow: "", sources: [] }), ["food", "dallas"]);
});

test("generic topics like weather do not count as Dallas", () => {
  assert.deepEqual(tagsForCard({ topics: ["work", "weather"], eyebrow: "", sources: [] }), ["career"]);
});

test("live cards map to tags through their subreddit", () => {
  const card = { topics: ["personalfinance"], eyebrow: "r/personalfinance", sources: [] };
  assert.deepEqual(tagsForCard(card), ["money"]);
});

test("source labels contribute subreddits", () => {
  const card = { topics: [], eyebrow: "Trend", sources: [{ label: "r/Fitness thread", url: "" }] };
  assert.deepEqual(cardSubreddits(card), ["fitness"]);
  assert.deepEqual(tagsForCard(card), ["health"]);
});

test("subscribed subreddits pre-select tags", () => {
  assert.deepEqual(tagsForSubreddits(["r/Python", "Dallas", "unknown"]), ["tech", "dallas"]);
});

test("stored tags keep their order and the retired local tag becomes Dallas", () => {
  assert.deepEqual(normalizeTags(["money", "local", "food", "dallas", "sports"]), ["money", "dallas", "food"]);
});

test("isTagId only accepts starter tags", () => {
  assert.equal(isTagId("food"), true);
  assert.equal(isTagId("sports"), false);
});
