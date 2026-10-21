import { useState } from "react";
import { Bookmark, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import SignalCover from "@/components/SignalCover";
import {
  recordInteraction,
  readStoredIds,
  SAVED_CARDS_KEY,
  setStoredId,
} from "@/services/interactions";
import type { ContentCard as ContentCardModel } from "@/types/content";

interface ContentCardProps {
  card: ContentCardModel;
}

const themeClasses: Record<ContentCardModel["theme"], string> = {
  coral: "card-theme-coral",
  ocean: "card-theme-ocean",
  lime: "card-theme-lime",
  gold: "card-theme-gold",
  violet: "card-theme-violet",
  ink: "card-theme-ink",
};

export default function ContentCard({ card }: ContentCardProps) {
  const [saved, setSaved] = useState(() => readStoredIds(SAVED_CARDS_KEY).includes(card.id));

  const toggleSaved = () => {
    const next = !saved;
    setStoredId(SAVED_CARDS_KEY, card.id, next);
    recordInteraction(card.id, next ? "save" : "unsave");
    setSaved(next);
  };

  return (
    <article className={`content-card ${themeClasses[card.theme]}`}>
      <Link
        to={`/signals/${card.id}`}
        state={{ card }}
        className="block focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-950/30"
        aria-label={`Open signal: ${card.headline}`}
      >
        <SignalCover card={card} />
        <div className="content-card-body">
          <span className="card-eyebrow">{card.eyebrow}</span>
          <h2 className="card-headline">{card.headline}</h2>
          <div className="card-preview-meta">
            <Sparkles className="h-3 w-3 shrink-0" />
            <span>{card.trendLabel}</span>
          </div>
        </div>
      </Link>

      <button
        type="button"
        onClick={toggleSaved}
        className="card-save-button"
        aria-label={saved ? "Remove from saved" : "Save signal"}
        title={saved ? "Saved" : "Save"}
      >
        <Bookmark className="h-4 w-4" fill={saved ? "currentColor" : "none"} />
      </button>
    </article>
  );
}
