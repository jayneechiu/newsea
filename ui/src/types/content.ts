export type FeedLane = "live" | "for-you" | "everyone" | "dallas" | "other-worlds";

export type CardType =
  | "trend"
  | "local-trend"
  | "community-insight"
  | "best-answer"
  | "story"
  | "worth-it";

export type CardTheme = "coral" | "ocean" | "lime" | "gold" | "violet" | "ink";

export interface CardSource {
  label: string;
  url: string;
}

export interface ContentCard {
  id: string;
  lane: FeedLane[];
  cardType: CardType;
  theme: CardTheme;
  eyebrow: string;
  headline: string;
  context: string;
  takeaways: string[];
  topics: string[];
  audience: string;
  sourceCount: number;
  communityCount: number;
  trendLabel: string;
  emailTeaser?: string;
  imageUrl?: string;
  coverEmoji?: string;
  sources: CardSource[];
  /** Translated copy, e.g. i18n.zh; missing fields fall back to English. */
  i18n?: { zh?: Partial<Pick<ContentCard, "eyebrow" | "headline" | "context" | "takeaways" | "trendLabel" | "emailTeaser">> };
}

export interface LiveSnapshot {
  updatedAt: string;
  cards: ContentCard[];
}
