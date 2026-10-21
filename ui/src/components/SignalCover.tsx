import { ArrowUpRight, Sparkles } from "lucide-react";
import type { ContentCard } from "@/types/content";

interface SignalCoverProps {
  card: ContentCard;
  detail?: boolean;
}

export default function SignalCover({ card, detail = false }: SignalCoverProps) {
  if (card.imageUrl) {
    return (
      <div className={detail ? "signal-cover signal-cover-detail" : "signal-cover"}>
        <img
          src={card.imageUrl.startsWith("/") ? `${import.meta.env.BASE_URL}${card.imageUrl.slice(1)}` : card.imageUrl}
          alt="" className="h-full w-full object-cover" />
        <div className="signal-cover-shade" />
        <span className="signal-cover-label">{card.trendLabel}</span>
      </div>
    );
  }

  return (
    <div className={`signal-cover signal-cover-fallback card-theme-${card.theme} ${detail ? "signal-cover-detail" : ""}`}>
      <div className="signal-cover-orbit" aria-hidden="true" />
      {card.coverEmoji ? (
        <span className="signal-cover-emoji" aria-hidden="true">{card.coverEmoji}</span>
      ) : (
        <Sparkles className="signal-cover-spark" aria-hidden="true" />
      )}
      <span className="signal-cover-label">{card.trendLabel}</span>
      <ArrowUpRight className="signal-cover-arrow" aria-hidden="true" />
    </div>
  );
}
