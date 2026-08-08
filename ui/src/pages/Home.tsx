import { useEffect, useState } from "react";
import { Compass, Mail, RefreshCw, Sparkles, Waves } from "lucide-react";
import { Link } from "react-router-dom";
import ContentCard from "@/components/ContentCard";
import { getContentFeed } from "@/services/feed";
import type { ContentCard as ContentCardModel, FeedLane } from "@/types/content";

const lanes: Array<{ id: FeedLane; label: string; shortLabel: string }> = [
  { id: "for-you", label: "For you", shortLabel: "For you" },
  { id: "everyone", label: "Everyone", shortLabel: "Everyone" },
  { id: "dallas", label: "Dallas", shortLabel: "Dallas" },
  { id: "other-worlds", label: "Other worlds", shortLabel: "Worlds" },
];

function readHiddenCards(): string[] {
  try {
    return JSON.parse(localStorage.getItem("newsea:hidden-cards") || "[]") as string[];
  } catch {
    return [];
  }
}

export default function Home() {
  const [activeLane, setActiveLane] = useState<FeedLane>("everyone");
  const [cards, setCards] = useState<ContentCardModel[]>([]);
  const [hiddenCards, setHiddenCards] = useState<string[]>(readHiddenCards);
  const [loading, setLoading] = useState(true);
  const [feedSource, setFeedSource] = useState<"api" | "mock" | "fallback">("mock");

  const loadFeed = async (lane: FeedLane) => {
    setLoading(true);
    const result = await getContentFeed(lane);
    setCards(result.cards);
    setFeedSource(result.source);
    setLoading(false);
  };

  useEffect(() => {
    void loadFeed(activeLane);
  }, [activeLane]);

  const hideCard = (cardId: string) => {
    const next = [...new Set([...hiddenCards, cardId])];
    localStorage.setItem("newsea:hidden-cards", JSON.stringify(next));
    setHiddenCards(next);
  };

  const visibleCards = cards.filter((card) => !hiddenCards.includes(card.id));

  return (
    <div className="min-h-screen bg-[#f4f1e9] text-slate-950">
      <header className="sticky top-0 z-50 border-b border-slate-950/10 bg-[#f4f1e9]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-3 sm:px-6">
          <a href="/" className="flex items-center gap-2.5" aria-label="Newsea home">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-white shadow-lg shadow-slate-950/15">
              <Waves className="h-5 w-5" />
            </span>
            <div>
              <div className="text-lg font-black leading-none tracking-[-0.04em]">newsea</div>
              <div className="mt-1 text-[9px] font-black uppercase tracking-[0.22em] text-slate-500">human signal feed</div>
            </div>
          </a>

          <div className="flex items-center gap-2">
            {feedSource !== "api" && (
              <span className="hidden rounded-full bg-amber-200 px-3 py-1.5 text-[10px] font-black uppercase tracking-wider text-amber-950 sm:inline-flex">
                Preview data
              </span>
            )}
            <Link
              to="/newsletter"
              className="hidden items-center gap-2 rounded-full border border-slate-950/15 bg-white px-4 py-2.5 text-xs font-extrabold transition hover:bg-slate-950 hover:text-white sm:inline-flex"
            >
              <Mail className="h-4 w-4" />
              Newsletter
            </Link>
            <button
              type="button"
              onClick={() => void loadFeed(activeLane)}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-950/15 bg-white transition hover:-rotate-12 hover:bg-slate-950 hover:text-white"
              aria-label="Refresh feed"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        <nav className="feed-nav mx-auto flex max-w-[1500px] gap-2 overflow-x-auto px-4 pb-3 sm:px-6" aria-label="Feed views">
          {lanes.map((lane) => (
            <button
              type="button"
              key={lane.id}
              onClick={() => setActiveLane(lane.id)}
              className={`shrink-0 rounded-full px-5 py-2.5 text-sm font-extrabold transition ${
                activeLane === lane.id
                  ? "bg-slate-950 text-white shadow-lg shadow-slate-950/15"
                  : "bg-white text-slate-600 hover:text-slate-950"
              }`}
            >
              <span className="sm:hidden">{lane.shortLabel}</span>
              <span className="hidden sm:inline">{lane.label}</span>
            </button>
          ))}
          <Link
            to="/newsletter"
            className="inline-flex shrink-0 items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-extrabold text-slate-600 sm:hidden"
          >
            <Mail className="h-4 w-4" />
            Digest
          </Link>
        </nav>
      </header>

      <main className="mx-auto max-w-[1500px] px-4 pb-20 pt-8 sm:px-6 sm:pt-12">
        <section className="mb-10 grid gap-6 border-b border-slate-950/15 pb-10 lg:grid-cols-[1.3fr_0.7fr] lg:items-end">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#dfff55] px-3 py-1.5 text-[11px] font-black uppercase tracking-[0.15em]">
              <Sparkles className="h-3.5 w-3.5" />
              Signal over noise
            </div>
            <h1 className="max-w-4xl text-4xl font-black leading-[0.95] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
              What people know,
              <br />
              before it becomes obvious.
            </h1>
          </div>
          <div className="max-w-xl lg:justify-self-end">
            <p className="text-base font-semibold leading-7 text-slate-600 sm:text-lg">
              The best conversations across Reddit, compressed into useful signals. No bait, no detours, no endless thread hunting.
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs font-black uppercase tracking-[0.12em] text-slate-500">
              <Compass className="h-4 w-4" />
              {lanes.find((lane) => lane.id === activeLane)?.label} · {visibleCards.length} signals
            </div>
          </div>
        </section>

        {loading && cards.length === 0 ? (
          <div className="columns-1 gap-5 sm:columns-2 lg:columns-3 xl:columns-4">
            {[280, 420, 340, 390, 310, 440, 360, 300].map((height, index) => (
              <div
                key={`${height}-${index}`}
                className="mb-5 animate-pulse break-inside-avoid rounded-[2rem] bg-slate-200"
                style={{ height }}
              />
            ))}
          </div>
        ) : (
          <div className="columns-1 gap-5 sm:columns-2 lg:columns-3 xl:columns-4">
            {visibleCards.map((card) => (
              <ContentCard key={card.id} card={card} onHide={hideCard} />
            ))}
          </div>
        )}

        {!loading && visibleCards.length === 0 && (
          <div className="rounded-[2rem] border border-dashed border-slate-950/25 bg-white p-12 text-center">
            <h2 className="text-2xl font-black">You cleared this view.</h2>
            <p className="mt-2 text-slate-500">Reset hidden cards to bring every signal back.</p>
            <button
              type="button"
              onClick={() => {
                localStorage.removeItem("newsea:hidden-cards");
                setHiddenCards([]);
              }}
              className="mt-6 rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white"
            >
              Reset cards
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
