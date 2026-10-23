import type { ContentCard } from "../types/content.ts";

export type TagId =
  | "food"
  | "money"
  | "career"
  | "tech"
  | "travel"
  | "style"
  | "family"
  | "culture"
  | "dallas"
  | "health";

export interface StarterTag {
  id: TagId;
  /** Lowercase ContentCard topics that belong to this tag. */
  topics: string[];
  /** Lowercase subreddit names (live cards use the subreddit as their only topic). */
  subreddits: string[];
}

/** Fixed, shared starter set; every user picks from the same tags. */
export const STARTER_TAGS: StarterTag[] = [
  { id: "food", topics: ["food", "kitchen"], subreddits: ["food", "cooking", "askculinary", "recipes", "dallasfood"] },
  { id: "money", topics: ["money"], subreddits: ["personalfinance", "henryfinance", "financialindependence", "frugal", "investing"] },
  {
    id: "career",
    topics: ["work", "career", "hiring", "management", "productivity"],
    subreddits: ["careerguidance", "cscareerquestions", "jobs", "antiwork", "flightattendants"],
  },
  { id: "tech", topics: ["software", "systems"], subreddits: ["programming", "technology", "python", "webdev", "machinelearning"] },
  { id: "travel", topics: ["travel", "commute", "etiquette"], subreddits: ["travel", "solotravel", "flights", "awardtravel"] },
  {
    id: "style",
    topics: ["style", "shopping", "crafts"],
    subreddits: ["femalefashionadvice", "malefashionadvice", "crafts", "buyitforlife"],
  },
  {
    id: "family",
    topics: ["parenting", "relationships", "life", "neighbors", "school"],
    subreddits: ["parenting", "relationship_advice", "mommit", "daddit"],
  },
  {
    id: "culture",
    topics: ["culture", "immigration", "books", "games", "story", "psychology"],
    subreddits: ["books", "gaming", "askreddit", "todayilearned", "china", "chinese"],
  },
  // shortcut: one hard-coded city, upgrade to user-searchable location tags when needed.
  {
    id: "dallas",
    topics: ["dallas", "local"],
    subreddits: ["dallas", "askdfw", "dfw", "fortworth", "plano", "frisco", "texas"],
  },
  { id: "health", topics: ["health", "fitness", "habits"], subreddits: ["fitness", "loseit", "nutrition", "getdisciplined"] },
];

const TAG_IDS = new Set<string>(STARTER_TAGS.map((tag) => tag.id));

export function isTagId(value: string): value is TagId {
  return TAG_IDS.has(value);
}

/** Clean a stored tag list: keep order, drop unknown ids and duplicates, map the retired "local" tag to Dallas. */
export function normalizeTags(raw: string[]): TagId[] {
  return [...new Set(raw.map((tag) => (tag === "local" ? "dallas" : tag)))].filter(isTagId);
}

const SUBREDDIT_PATTERN = /\br\/([A-Za-z0-9_]+)/g;

/** Lowercase subreddit names a card cites in its eyebrow or source labels. */
export function cardSubreddits(card: Pick<ContentCard, "eyebrow" | "sources">): string[] {
  const text = [card.eyebrow, ...card.sources.map((source) => source.label)].join(" ");
  return [...text.matchAll(SUBREDDIT_PATTERN)].map((match) => match[1].toLowerCase());
}

export function tagsForCard(card: Pick<ContentCard, "topics" | "eyebrow" | "sources">): TagId[] {
  const signals = new Set([...card.topics.map((topic) => topic.toLowerCase()), ...cardSubreddits(card)]);
  return STARTER_TAGS.filter(
    (tag) => tag.topics.some((topic) => signals.has(topic)) || tag.subreddits.some((sub) => signals.has(sub)),
  ).map((tag) => tag.id);
}

/** Pre-select tags from a list of subreddits (e.g. a future Reddit login's subscriptions). */
export function tagsForSubreddits(subreddits: string[]): TagId[] {
  const names = new Set(subreddits.map((name) => name.toLowerCase().replace(/^\/?r\//, "")));
  return STARTER_TAGS.filter((tag) => tag.subreddits.some((sub) => names.has(sub))).map((tag) => tag.id);
}
