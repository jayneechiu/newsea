export type FeedLane = "for-you" | "everyone" | "dallas" | "other-worlds";

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
  sources: CardSource[];
}
