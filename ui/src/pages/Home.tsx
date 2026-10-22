import { useEffect, useState } from "react";
import { Compass, Mail, RefreshCw, Sparkles, Waves } from "lucide-react";
import { Link } from "react-router-dom";
import ContentCard from "@/components/ContentCard";
import LanguageToggle from "@/components/LanguageToggle";
import { useI18n, type MessageKey } from "@/i18n";
import { getContentFeed, getLiveSnapshot } from "@/services/feed";
import type { ContentCard as ContentCardModel, FeedLane } from "@/types/content";

const lanes: Array<{ id: FeedLane; label: MessageKey; shortLabel: MessageKey }> = [
  { id: "live", label: "laneLive", shortLabel: "laneLiveShort" },
  { id: "for-you", label: "laneForYou", shortLabel: "laneForYou" },
  { id: "everyone", label: "laneEveryone", shortLabel: "laneEveryone" },
  { id: "dallas", label: "laneDallas", shortLabel: "laneDallas" },
  { id: "other-worlds", label: "laneOtherWorlds", shortLabel: "laneOtherWorldsShort" },
];

function readHiddenCards(): string[] {
  try {
    return JSON.parse(localStorage.getItem("newsea:hidden-cards") || "[]") as string[];
  } catch {
    return [];
  }
}

export default function Home() {
  const { lang, t } = useI18n();
  const [activeLane, setActiveLane] = useState<FeedLane>("everyone");
  const [cards, setCards] = useState<ContentCardModel[]>([]);
  const [hiddenCards, setHiddenCards] = useState<string[]>(readHiddenCards);
  const [loading, setLoading] = useState(true);
  const [feedSource, setFeedSource] = useState<"api" | "mock" | "fallback" | "live">("mock");
  const [refreshRound, setRefreshRound] = useState(0);
  const [liveUpdatedAt, setLiveUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    void getLiveSnapshot().then((snapshot) => setLiveUpdatedAt(snapshot?.updatedAt ?? null));
  }, []);

  const visibleLanes = lanes.filter((lane) => lane.id !== "live" || liveUpdatedAt);
  const liveDate = liveUpdatedAt
    ? new Date(liveUpdatedAt).toLocaleDateString(lang === "zh" ? "zh-CN" : "en-US", { month: "short", day: "numeric" })
    : "";

  const loadFeed = async (lane: FeedLane, round: number) => {
    setLoading(true);
    const result = await getContentFeed(lane, round);
    setCards(result.cards);
    setFeedSource(result.source);
    setLoading(false);
  };

  useEffect(() => {
    void loadFeed(activeLane, refreshRound);
  }, [activeLane, refreshRound]);

  const visibleCards = cards.filter((card) => !hiddenCards.includes(card.id));

  return (
    <div className="min-h-screen bg-[#f4f1e9] text-slate-950">
      <header className="sticky top-0 z-50 border-b border-slate-950/10 bg-[#f4f1e9]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-3 sm:px-6">
          <a href={import.meta.env.BASE_URL} className="flex items-center gap-2.5" aria-label="Newsea home">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-white shadow-lg shadow-slate-950/15">
              <Waves className="h-5 w-5" />
            </span>
            <div>
              <div className="text-lg font-black leading-none tracking-[-0.04em]">newsea</div>
              <div className="mt-1 text-[9px] font-black uppercase tracking-[0.22em] text-slate-500">{t("tagline")}</div>
            </div>
          </a>

          <div className="flex items-center gap-2">
            {(feedSource === "mock" || feedSource === "fallback") && (
              <span className="hidden rounded-full bg-amber-200 px-3 py-1.5 text-[10px] font-black uppercase tracking-wider text-amber-950 sm:inline-flex">
                {t("previewData")}
              </span>
            )}
            <LanguageToggle />
            <Link
              to="/newsletter"
              className="hidden items-center gap-2 rounded-full border border-slate-950/15 bg-white px-4 py-2.5 text-xs font-extrabold transition hover:bg-slate-950 hover:text-white sm:inline-flex"
            >
              <Mail className="h-4 w-4" />
              {t("newsletter")}
            </Link>
            <button
              type="button"
              onClick={() => setRefreshRound((round) => round + 1)}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-950/15 bg-white transition hover:-rotate-12 hover:bg-slate-950 hover:text-white"
              aria-label={t("refreshFeed")}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        <nav className="feed-nav mx-auto flex max-w-[1500px] gap-2 overflow-x-auto px-4 pb-3 sm:px-6" aria-label={t("feedViews")}>
          {visibleLanes.map((lane) => (
            <button
              type="button"
              key={lane.id}
              onClick={() => setActiveLane(lane.id)}
              className={`inline-flex shrink-0 items-center gap-2 rounded-full px-5 py-2.5 text-sm font-extrabold transition ${
                activeLane === lane.id
                  ? "bg-slate-950 text-white shadow-lg shadow-slate-950/15"
                  : "bg-white text-slate-600 hover:text-slate-950"
              }`}
            >
              {lane.id === "live" && <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" aria-hidden="true" />}
              <span className="sm:hidden">{t(lane.shortLabel)}</span>
              <span className="hidden sm:inline">{t(lane.label)}</span>
            </button>
          ))}
          <Link
            to="/newsletter"
            className="inline-flex shrink-0 items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-extrabold text-slate-600 sm:hidden"
          >
            <Mail className="h-4 w-4" />
            {t("digest")}
          </Link>
        </nav>
      </header>

      <main className="mx-auto max-w-[1500px] px-3 pb-20 pt-6 sm:px-6 sm:pt-12">
        <section className="mb-6 grid gap-4 border-b border-slate-950/15 pb-6 sm:mb-10 sm:gap-6 sm:pb-10 lg:grid-cols-[1.3fr_0.7fr] lg:items-end">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#dfff55] px-3 py-1.5 text-[11px] font-black uppercase tracking-[0.15em]">
              <Sparkles className="h-3.5 w-3.5" />
              {t("heroBadge")}
            </div>
            <h1 className="max-w-4xl text-[2.35rem] font-black leading-[0.95] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
              {t("heroLine1")}
              <br />
              {t("heroLine2")}
            </h1>
          </div>
          <div className="max-w-xl lg:justify-self-end">
            <p className="hidden text-base font-semibold leading-7 text-slate-600 sm:block sm:text-lg">
              {t("heroBody")}
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs font-black uppercase tracking-[0.12em] text-slate-500">
              <Compass className="h-4 w-4" />
              {t(lanes.find((lane) => lane.id === activeLane)?.label ?? "laneEveryone")} · {t("signalsCount", { count: visibleCards.length })}
            </div>
            {activeLane === "live" && liveDate && (
              <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-[11px] font-black uppercase tracking-[0.1em] text-emerald-900">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden="true" />
                {t("liveUpdated", { date: liveDate })}
              </div>
            )}
          </div>
        </section>

        {loading && cards.length === 0 ? (
          <div className="columns-2 gap-2.5 sm:gap-5 lg:columns-3 xl:columns-4">
            {[280, 420, 340, 390, 310, 440, 360, 300].map((height, index) => (
              <div
                key={`${height}-${index}`}
                className="mb-2.5 animate-pulse break-inside-avoid rounded-[1.25rem] bg-slate-200 sm:mb-5 sm:rounded-[2rem]"
                style={{ height: Math.max(210, Math.round(height * 0.68)) }}
              />
            ))}
          </div>
        ) : (
          <div className="columns-2 gap-2.5 sm:gap-5 lg:columns-3 xl:columns-4">
            {visibleCards.map((card) => (
              <ContentCard key={card.id} card={card} />
            ))}
          </div>
        )}

        {!loading && visibleCards.length === 0 && (
          <div className="rounded-[2rem] border border-dashed border-slate-950/25 bg-white p-12 text-center">
            <h2 className="text-2xl font-black">{t("clearedTitle")}</h2>
            <p className="mt-2 text-slate-500">{t("clearedBody")}</p>
            <button
              type="button"
              onClick={() => {
                localStorage.removeItem("newsea:hidden-cards");
                setHiddenCards([]);
              }}
              className="mt-6 rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white"
            >
              {t("resetCards")}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
