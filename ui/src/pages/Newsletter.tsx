import { FormEvent, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Check, Clock3, Mail, Send, Waves } from "lucide-react";
import { Link } from "react-router-dom";
import { getContentFeed } from "@/services/feed";
import { getLatestNewsletter, subscribe, type NewsletterPost } from "@/services/api";
import type { ContentCard } from "@/types/content";

type SubscribeState = "idle" | "submitting" | "pending" | "error";

export default function Newsletter() {
  const [cards, setCards] = useState<ContentCard[]>([]);
  const [livePosts, setLivePosts] = useState<NewsletterPost[]>([]);
  const [editorWords, setEditorWords] = useState("");
  const [subscribeState, setSubscribeState] = useState<SubscribeState>("idle");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const sendEnabled = import.meta.env.VITE_ENABLE_NEWSLETTER_SEND === "true";

  useEffect(() => {
    void getContentFeed("everyone").then((result) => setCards(result.cards.slice(0, 4)));
    void getLatestNewsletter()
      .then((result) => {
        setLivePosts(result.posts.slice(0, 4));
        setEditorWords(result.editor_words);
      })
      .catch(() => {
        // The curated demo remains the public fallback until a draft is sent.
      });
  }, []);

  const topics = livePosts.length
    ? livePosts.map((post) => ({
        id: post.id,
        eyebrow: `r/${post.subreddit}`,
        headline: post.title,
        teaser: post.newsletter_teaser || post.gpt_summary || post.selftext || "Open the original conversation.",
        trendLabel: post.trend_label,
        url: post.permalink,
      }))
    : cards.map((card) => ({
        id: card.id,
        eyebrow: card.eyebrow,
        headline: card.headline,
        teaser: card.emailTeaser || card.context,
        trendLabel: card.trendLabel,
        url: card.sources[0]?.url || "/",
      }));

  const handleSubscribe = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubscribeState("submitting");
    try {
      await subscribe(email, ["todayilearned", "AskReddit", "technology"], name || undefined);
      setSubscribeState("pending");
    } catch {
      setSubscribeState("error");
    }
  };

  return (
    <div className="min-h-screen bg-[#e8e0d2] text-slate-950">
      <header className="border-b border-slate-950/15 bg-[#f4f1e9]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2.5" aria-label="Back to Newsea feed">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-white">
              <Waves className="h-5 w-5" />
            </span>
            <div>
              <div className="text-lg font-black leading-none tracking-[-0.04em]">newsea</div>
              <div className="mt-1 text-[9px] font-black uppercase tracking-[0.22em] text-slate-500">human signal feed</div>
            </div>
          </Link>

          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-extrabold shadow-sm transition hover:bg-slate-950 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Live feed
          </Link>
        </div>
      </header>

      <main>
        <section className="border-b border-slate-950/15 px-4 py-16 sm:px-6 sm:py-24">
          <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full border border-slate-950/15 bg-[#ffc94a] px-3 py-1.5 text-[10px] font-black uppercase tracking-[0.16em]">
                <Mail className="h-3.5 w-3.5" />
                The original Newsea format
              </span>
              <h1 className="mt-5 max-w-3xl text-5xl font-black leading-[0.92] tracking-[-0.06em] sm:text-7xl">
                The signal,
                <br />
                delivered slowly.
              </h1>
            </div>
            <div className="max-w-lg lg:justify-self-end">
              <p className="text-lg font-semibold leading-8 text-slate-600">
                Newsea began as a Reddit newsletter. The visual feed is now the primary product, but the digest remains a useful way to revisit the week without another infinite scroll.
              </p>
              <p className="mt-4 text-sm font-bold uppercase tracking-[0.12em] text-slate-500">
                A preserved product chapter · not a dead feature
              </p>
            </div>
          </div>
        </section>

        <section className="px-4 py-12 sm:px-6 sm:py-16">
          <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
            <article className="overflow-hidden rounded-[2rem] bg-[#fffdf7] shadow-[0_30px_90px_rgba(30,25,20,0.16)]">
              <div className="border-b border-slate-950/10 bg-slate-950 px-6 py-4 text-white sm:px-10">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-sm font-black uppercase tracking-[0.18em]">Newsea Weekly</span>
                  <span className="text-xs font-bold text-white/60">Preview edition</span>
                </div>
              </div>

              <div className="px-6 py-9 sm:px-10 sm:py-12">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-orange-600">Editor's signal</p>
                <h2 className="mt-3 max-w-3xl text-3xl font-black leading-tight tracking-[-0.04em] sm:text-5xl">
                  Four conversations worth carrying into next week.
                </h2>
                <p className="mt-5 max-w-2xl text-base font-medium leading-7 text-slate-600">
                  {editorWords || "No timeline anxiety. Just enough context, a curious hook, and a path back to the original discussion."}
                </p>

                <div className="mt-10 divide-y divide-slate-950/10 border-y border-slate-950/10">
                  {topics.map((topic) => (
                    <div key={topic.id} className="grid gap-4 py-7 sm:grid-cols-[1fr_auto] sm:items-start">
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">{topic.eyebrow}</p>
                        <h3 className="mt-2 text-xl font-black leading-tight tracking-[-0.025em]">{topic.headline}</h3>
                        <p className="mt-2 text-sm font-medium leading-6 text-slate-600">{topic.teaser}</p>
                        <a href={topic.url} target="_blank" rel="noreferrer" className="mt-3 inline-flex text-xs font-black uppercase tracking-wide text-orange-700">See the conversation →</a>
                      </div>
                      {topic.trendLabel && <span className="hidden rounded-full bg-[#dfff55] px-3 py-1.5 text-[10px] font-black uppercase tracking-wide sm:inline-flex">{topic.trendLabel}</span>}
                    </div>
                  ))}
                </div>

                <Link
                  to="/"
                  className="mt-9 inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-extrabold text-white transition hover:bg-slate-700"
                >
                  Explore every signal
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </article>

            <aside className="space-y-5">
              <form onSubmit={handleSubscribe} className="rounded-[2rem] bg-slate-950 p-6 text-white shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-[0.16em] text-[#dfff55]">Request an invite</p>
                <h2 className="mt-3 text-2xl font-black leading-tight tracking-[-0.04em]">A quiet digest, with a human at the door.</h2>
                <p className="mt-3 text-sm font-medium leading-6 text-white/65">
                  Every request is reviewed by Newsea's owner. Applying does not add you to a mailing list yet.
                </p>
                {subscribeState === "pending" ? (
                  <div className="mt-5 rounded-2xl bg-white/10 p-4">
                    <p className="flex items-center gap-2 text-sm font-extrabold text-[#dfff55]"><Clock3 className="h-4 w-4" /> Awaiting approval</p>
                    <p className="mt-2 text-sm leading-6 text-white/70">Your request is saved. No newsletter will be sent until it is approved.</p>
                  </div>
                ) : (
                  <>
                    <label htmlFor="newsletter-name" className="mt-5 block text-xs font-extrabold">Name <span className="text-white/45">(optional)</span></label>
                    <input id="newsletter-name" value={name} onChange={(event) => setName(event.target.value)} className="mt-2 w-full rounded-xl border border-white/15 bg-white/10 px-3 py-2.5 text-sm font-semibold outline-none placeholder:text-white/35 focus:ring-2 focus:ring-[#dfff55]" placeholder="How should we greet you?" />
                    <label htmlFor="newsletter-email" className="mt-4 block text-xs font-extrabold">Email</label>
                    <input id="newsletter-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-xl border border-white/15 bg-white/10 px-3 py-2.5 text-sm font-semibold outline-none placeholder:text-white/35 focus:ring-2 focus:ring-[#dfff55]" placeholder="you@example.com" required />
                    <button type="submit" disabled={subscribeState === "submitting"} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-[#dfff55] px-4 py-3 text-sm font-black text-slate-950 disabled:opacity-50">
                      <Mail className="h-4 w-4" />
                      {subscribeState === "submitting" ? "Requesting…" : "Request approval"}
                    </button>
                    {subscribeState === "error" && <p className="mt-3 text-sm font-bold text-red-300">Could not save the request. Please try again.</p>}
                  </>
                )}
              </form>

              <div className="rounded-[2rem] bg-[#dfff55] p-6">
                <p className="text-[10px] font-black uppercase tracking-[0.16em]">Why keep it?</p>
                <h2 className="mt-3 text-2xl font-black leading-tight tracking-[-0.04em]">One pipeline, two consumption speeds.</h2>
                <ul className="mt-5 space-y-3 text-sm font-semibold leading-5">
                  {["The feed drives discovery.", "The digest supports reflection.", "Both use the same ContentCards."].map((item) => (
                    <li key={item} className="flex gap-2">
                      <Check className="mt-0.5 h-4 w-4 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {sendEnabled ? (
                <div className="rounded-[2rem] bg-white p-6 shadow-sm">
                  <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">Local owner controls</p>
                  <p className="mt-3 text-sm font-semibold leading-6 text-slate-600">Generate a GPT-written draft, inspect every hook, review subscribers, then send the exact saved edition.</p>
                  <Link to="/newsletter/admin" className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-extrabold text-white">
                    <Send className="h-4 w-4" />
                    Open owner desk
                  </Link>
                </div>
              ) : (
                <div className="rounded-[2rem] border border-slate-950/10 bg-white/60 p-6">
                  <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">Public preview safety</p>
                  <p className="mt-3 text-sm font-semibold leading-6 text-slate-600">
                    Email sending is hidden in public builds. Owners can enable the connected controls locally with
                    <code className="mx-1 rounded bg-white px-1.5 py-1 text-xs text-slate-900">VITE_ENABLE_NEWSLETTER_SEND=true</code>.
                  </p>
                </div>
              )}
            </aside>
          </div>
        </section>
      </main>
    </div>
  );
}
