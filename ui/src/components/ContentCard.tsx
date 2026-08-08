import { useState } from "react";
import {
  Bookmark,
  ChevronDown,
  ExternalLink,
  EyeOff,
  Layers3,
  Sparkles,
} from "lucide-react";
import type { ContentCard as ContentCardModel } from "@/types/content";

interface ContentCardProps {
  card: ContentCardModel;
  onHide: (cardId: string) => void;
}

const themeClasses: Record<ContentCardModel["theme"], string> = {
  coral: "card-theme-coral",
  ocean: "card-theme-ocean",
  lime: "card-theme-lime",
  gold: "card-theme-gold",
  violet: "card-theme-violet",
  ink: "card-theme-ink",
};

function readSavedCards(): string[] {
  try {
    return JSON.parse(localStorage.getItem("newsea:saved-cards") || "[]") as string[];
  } catch {
    return [];
  }
}

export default function ContentCard({ card, onHide }: ContentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [saved, setSaved] = useState(() => readSavedCards().includes(card.id));

  const toggleSaved = () => {
    const current = new Set(readSavedCards());
    if (saved) current.delete(card.id);
    else current.add(card.id);
    localStorage.setItem("newsea:saved-cards", JSON.stringify([...current]));
    setSaved(!saved);
  };

  return (
    <article className={`content-card ${themeClasses[card.theme]}`}>
      <div className="content-card-noise" aria-hidden="true" />

      <div className="relative z-10">
        <div className="mb-5 flex items-start justify-between gap-3">
          <span className="card-eyebrow">{card.eyebrow}</span>
          <button
            type="button"
            onClick={toggleSaved}
            className="card-icon-button"
            aria-label={saved ? "Remove from saved" : "Save card"}
            title={saved ? "Saved" : "Save"}
          >
            <Bookmark className="h-4 w-4" fill={saved ? "currentColor" : "none"} />
          </button>
        </div>

        <h2 className="card-headline">{card.headline}</h2>
        <p className="card-context">
          {card.context}
        </p>

        <div className="card-meta">
          <span className="inline-flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5" />
            {card.trendLabel}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Layers3 className="h-3.5 w-3.5" />
            {card.communityCount} communities · {card.sourceCount} sources
          </span>
        </div>

        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="mt-5 flex w-full items-center justify-between rounded-2xl bg-white/50 px-4 py-3 text-left text-sm font-extrabold transition hover:bg-white/70"
          aria-expanded={expanded}
        >
          <span>{expanded ? "Close the signal" : "See the signal"}</span>
          <ChevronDown
            className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`}
          />
        </button>

        {expanded && (
          <div className="mt-4 animate-card-reveal rounded-2xl bg-white/70 p-4 text-slate-900 shadow-sm">
            <ol className="space-y-3">
              {card.takeaways.map((takeaway, index) => (
                <li key={takeaway} className="flex gap-3 text-sm font-medium leading-5">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-900 text-[11px] font-black text-white">
                    {index + 1}
                  </span>
                  <span className="pt-0.5">{takeaway}</span>
                </li>
              ))}
            </ol>

            <div className="mt-5 flex flex-wrap gap-2 border-t border-slate-900/10 pt-4">
              {card.sources.map((source) => (
                <a
                  key={source.url}
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-slate-700"
                >
                  {source.label}
                  <ExternalLink className="h-3 w-3" />
                </a>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          <div className="flex flex-wrap gap-1.5">
            {card.topics.slice(0, 3).map((topic) => (
              <span key={topic} className="card-topic">
                {topic}
              </span>
            ))}
          </div>
          <button
            type="button"
            onClick={() => onHide(card.id)}
            className="card-icon-button"
            aria-label="Show less like this"
            title="Less like this"
          >
            <EyeOff className="h-4 w-4" />
          </button>
        </div>
      </div>
    </article>
  );
}
