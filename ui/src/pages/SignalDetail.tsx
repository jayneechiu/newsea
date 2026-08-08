import { useMemo, useState } from "react";
import {
  ArrowLeft,
  Bookmark,
  ExternalLink,
  EyeOff,
  Heart,
  Layers3,
  Sparkles,
  Waves,
} from "lucide-react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import ContentCard from "@/components/ContentCard";
import SignalCover from "@/components/SignalCover";
import { getContentCardById, getRelatedContentCards } from "@/services/feed";
import {
  HIDDEN_CARDS_KEY,
  LIKED_CARDS_KEY,
  recordInteraction,
  readStoredIds,
  SAVED_CARDS_KEY,
  setStoredId,
} from "@/services/interactions";
import type { ContentCard as ContentCardModel } from "@/types/content";

interface SignalLocationState {
  card?: ContentCardModel;
}

export default function SignalDetail() {
  const { cardId = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const routeCard = (location.state as SignalLocationState | null)?.card;
  const card = routeCard?.id === cardId ? routeCard : getContentCardById(cardId);
  const [liked, setLiked] = useState(() => readStoredIds(LIKED_CARDS_KEY).includes(cardId));
  const [saved, setSaved] = useState(() => readStoredIds(SAVED_CARDS_KEY).includes(cardId));
  const related = useMemo(() => (card ? getRelatedContentCards(card) : []), [card]);

  if (!card) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f4f1e9] px-6 text-center">
        <div>
          <div className="text-5xl">🌊</div>
          <h1 className="mt-5 text-3xl font-black tracking-tight">This signal drifted away.</h1>
          <p className="mt-2 text-slate-500">It may have expired from this session.</p>
          <Link to="/" className="mt-6 inline-flex rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white">
            Back to the feed
          </Link>
        </div>
      </main>
    );
  }

  const toggleLike = () => {
    const next = !liked;
    setStoredId(LIKED_CARDS_KEY, card.id, next);
    recordInteraction(card.id, next ? "like" : "unlike");
    setLiked(next);
  };

  const toggleSaved = () => {
    const next = !saved;
    setStoredId(SAVED_CARDS_KEY, card.id, next);
    recordInteraction(card.id, next ? "save" : "unsave");
    setSaved(next);
  };

  const hideSignal = () => {
    setStoredId(HIDDEN_CARDS_KEY, card.id, true);
    recordInteraction(card.id, "hide");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-[#f4f1e9] text-slate-950">
      <header className="sticky top-0 z-50 border-b border-slate-950/10 bg-[#f4f1e9]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <Link to="/" className="inline-flex items-center gap-2 text-sm font-extrabold">
            <span className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-950/15 bg-white">
              <ArrowLeft className="h-4 w-4" />
            </span>
            <span className="hidden sm:inline">Back to signals</span>
          </Link>
          <Link to="/" className="flex items-center gap-2 font-black tracking-[-0.04em]">
            <Waves className="h-5 w-5" />
            newsea
          </Link>
          <button
            type="button"
            onClick={hideSignal}
            className="inline-flex h-9 items-center gap-2 rounded-full border border-slate-950/15 bg-white px-3 text-xs font-bold text-slate-600 transition hover:text-slate-950"
            aria-label="Show fewer signals like this"
          >
            <EyeOff className="h-4 w-4" />
            <span className="hidden sm:inline">Less like this</span>
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pb-24 pt-5 sm:px-6 sm:pt-10">
        <article>
          <SignalCover card={card} detail />

          <div className="mx-auto max-w-4xl">
            <div className="-mt-8 relative z-10 rounded-[1.75rem] bg-white p-5 shadow-[0_20px_70px_rgba(15,23,42,0.12)] sm:-mt-16 sm:rounded-[2.5rem] sm:p-10">
              <div className="flex items-start justify-between gap-4">
                <span className="detail-eyebrow">{card.eyebrow}</span>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={toggleLike}
                    className={`detail-action ${liked ? "detail-action-active" : ""}`}
                    aria-pressed={liked}
                    aria-label={liked ? "Unlike signal" : "Like signal"}
                  >
                    <Heart className="h-5 w-5" fill={liked ? "currentColor" : "none"} />
                    <span>{liked ? "Liked" : "Like"}</span>
                  </button>
                  <button
                    type="button"
                    onClick={toggleSaved}
                    className={`detail-action ${saved ? "detail-action-active" : ""}`}
                    aria-pressed={saved}
                    aria-label={saved ? "Remove signal from saved" : "Save signal"}
                  >
                    <Bookmark className="h-5 w-5" fill={saved ? "currentColor" : "none"} />
                    <span>{saved ? "Saved" : "Save"}</span>
                  </button>
                </div>
              </div>

              <h1 className="mt-6 text-[2.3rem] font-black leading-[0.96] tracking-[-0.055em] sm:text-6xl">
                {card.headline}
              </h1>
              <p className="mt-5 max-w-3xl text-lg font-semibold leading-8 text-slate-600 sm:text-xl">
                {card.context}
              </p>

              <div className="mt-7 flex flex-wrap gap-3 border-y border-slate-950/10 py-5 text-xs font-black uppercase tracking-[0.1em] text-slate-500">
                <span className="inline-flex items-center gap-2"><Sparkles className="h-4 w-4" />{card.trendLabel}</span>
                <span className="inline-flex items-center gap-2"><Layers3 className="h-4 w-4" />{card.communityCount} communities · {card.sourceCount} sources</span>
              </div>

              <section className="mt-9">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Why it matters</p>
                <ol className="mt-5 space-y-4">
                  {card.takeaways.map((takeaway, index) => (
                    <li key={takeaway} className="flex gap-4 rounded-2xl bg-[#f4f1e9] p-4 text-base font-bold leading-6 sm:p-5">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-950 text-xs font-black text-white">{index + 1}</span>
                      <span className="pt-1">{takeaway}</span>
                    </li>
                  ))}
                </ol>
              </section>

              <section className="mt-10 grid gap-8 border-t border-slate-950/10 pt-8 sm:grid-cols-2">
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Communities sampled</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {card.sources.map((source) => (
                      <a key={source.url} href={source.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-2.5 text-sm font-bold text-white">
                        {source.label}<ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Filed under</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {card.topics.map((topic) => <span key={topic} className="rounded-full border border-slate-950/15 px-3 py-2 text-sm font-bold">#{topic}</span>)}
                  </div>
                </div>
              </section>
            </div>
          </div>
        </article>

        {related.length > 0 && (
          <section className="mt-16">
            <div className="mb-6 flex items-end justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Keep exploring</p>
                <h2 className="mt-2 text-3xl font-black tracking-[-0.04em]">Signals with the same current</h2>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
              {related.map((relatedCard) => <ContentCard key={relatedCard.id} card={relatedCard} />)}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
