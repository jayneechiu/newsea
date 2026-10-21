import { FormEvent, useState } from "react";
import { ArrowLeft, Check, KeyRound, RefreshCw, Send, Sparkles, X } from "lucide-react";
import { Link } from "react-router-dom";
import {
  getNewsletterSubscriptions,
  reviewNewsletterSubscription,
  createNewsletterDraft,
  sendNewsletterDraft,
  type NewsletterDraft,
  type NewsletterSubscription,
} from "@/services/api";

export default function NewsletterAdmin() {
  const [adminKey, setAdminKey] = useState("");
  const [subscriptions, setSubscriptions] = useState<NewsletterSubscription[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [subreddit, setSubreddit] = useState("todayilearned");
  const [draft, setDraft] = useState<NewsletterDraft | null>(null);
  const [draftLoading, setDraftLoading] = useState(false);

  const loadPending = async (event?: FormEvent) => {
    event?.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const result = await getNewsletterSubscriptions(adminKey, "pending");
      setSubscriptions(result.subscriptions);
      setMessage(result.count ? "Pending requests loaded." : "No pending requests.");
    } catch {
      setMessage("Could not load requests. Check the admin key and API connection.");
    } finally {
      setLoading(false);
    }
  };

  const review = async (id: number, action: "approve" | "reject") => {
    try {
      await reviewNewsletterSubscription(id, action, adminKey);
      setSubscriptions((items) => items.filter((item) => item.id !== id));
      setMessage(action === "approve" ? "Subscriber approved." : "Request rejected.");
    } catch {
      setMessage("Review failed. Refresh and try again.");
    }
  };

  const generateDraft = async () => {
    setDraftLoading(true);
    setMessage("Fetching Reddit once and writing the Newsea hooks…");
    try {
      const result = await createNewsletterDraft(subreddit, adminKey);
      setDraft(result.draft);
      setMessage("Draft ready. Preview these exact words before sending.");
    } catch {
      setMessage("Draft generation failed. Check the key and backend logs.");
    } finally {
      setDraftLoading(false);
    }
  };

  const sendDraft = async () => {
    if (!draft) return;
    setDraftLoading(true);
    try {
      await sendNewsletterDraft(draft.id, adminKey);
      setDraft({ ...draft, status: "sending" });
      setMessage("Sending this saved draft to approved subscribers only.");
    } catch {
      setMessage("Send did not start. Make sure at least one subscriber is approved.");
    } finally {
      setDraftLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#e8e0d2] px-4 py-8 text-slate-950 sm:px-6 sm:py-14">
      <div className="mx-auto max-w-4xl">
        <Link to="/newsletter" className="inline-flex items-center gap-2 text-sm font-extrabold"><ArrowLeft className="h-4 w-4" /> Newsletter</Link>
        <div className="mt-7 rounded-[2rem] bg-[#fffdf7] p-6 shadow-[0_30px_90px_rgba(30,25,20,0.14)] sm:p-10">
          <p className="text-[10px] font-black uppercase tracking-[0.16em] text-orange-600">Owner only</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.05em] sm:text-5xl">Subscriber approvals</h1>
          <p className="mt-3 max-w-2xl text-sm font-semibold leading-6 text-slate-600">The key stays in this page's memory and is sent only as an admin request header. It is never bundled into the public app.</p>
          <form onSubmit={loadPending} className="mt-7 flex flex-col gap-3 sm:flex-row">
            <label className="relative flex-1">
              <KeyRound className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
              <input type="password" value={adminKey} onChange={(event) => setAdminKey(event.target.value)} placeholder="Newsletter admin key" className="w-full rounded-xl border border-slate-950/15 bg-white py-2.5 pl-10 pr-3 text-sm font-semibold outline-none focus:ring-2 focus:ring-slate-950" required />
            </label>
            <button disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-extrabold text-white disabled:opacity-50"><RefreshCw className="h-4 w-4" /> {loading ? "Loading…" : "Load pending"}</button>
          </form>
          {message && <p className="mt-4 text-sm font-bold text-slate-600">{message}</p>}

          <section className="mt-8 rounded-2xl bg-slate-950 p-5 text-white sm:p-6">
            <p className="text-[10px] font-black uppercase tracking-[0.16em] text-[#dfff55]">Reusable edition</p>
            <h2 className="mt-2 text-2xl font-black tracking-[-0.04em]">Generate once. Preview and send the same draft.</h2>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <input value={subreddit} onChange={(event) => setSubreddit(event.target.value)} className="flex-1 rounded-xl border border-white/15 bg-white/10 px-3 py-2.5 text-sm font-semibold outline-none focus:ring-2 focus:ring-[#dfff55]" aria-label="Subreddit for newsletter draft" required />
              <button type="button" onClick={generateDraft} disabled={!adminKey || draftLoading} className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#dfff55] px-5 py-2.5 text-sm font-black text-slate-950 disabled:opacity-50"><Sparkles className="h-4 w-4" /> {draftLoading ? "Working…" : "Generate draft"}</button>
            </div>
            {draft && (
              <div className="mt-6 space-y-3">
                <p className={`inline-flex rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-wide ${draft.uses_ai ? "bg-[#dfff55] text-slate-950" : "bg-amber-300 text-slate-950"}`}>
                  {draft.uses_ai ? "GPT copy ready" : "Fallback copy — do not send without review"}
                </p>
                <p className="text-sm font-bold leading-6 text-white/70">{draft.editor_words}</p>
                {draft.posts.map((post) => (
                  <article key={post.id} className="rounded-xl bg-white/10 p-4">
                    <p className="text-[10px] font-black uppercase tracking-wide text-[#dfff55]">r/{post.subreddit}</p>
                    <h3 className="mt-2 font-black leading-tight">{post.title}</h3>
                    <p className="mt-2 text-sm font-medium leading-6 text-white/70">{post.newsletter_teaser}</p>
                  </article>
                ))}
                <button type="button" onClick={sendDraft} disabled={draftLoading || draft.status !== "draft"} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#ff8f70] px-5 py-3 text-sm font-black text-slate-950 disabled:opacity-50"><Send className="h-4 w-4" /> Send this exact draft</button>
              </div>
            )}
          </section>

          <div className="mt-7 space-y-3">
            {subscriptions.map((subscription) => (
              <article key={subscription.id} className="flex flex-col gap-4 rounded-2xl border border-slate-950/10 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-black">{subscription.name || "Unnamed reader"}</p>
                  <p className="mt-1 text-sm font-semibold text-slate-600">{subscription.email}</p>
                  <p className="mt-2 text-xs font-bold text-slate-400">Requested {new Date(subscription.requested_at).toLocaleString()}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => review(subscription.id, "approve")} className="inline-flex items-center gap-2 rounded-xl bg-[#dfff55] px-4 py-2.5 text-sm font-black"><Check className="h-4 w-4" /> Approve</button>
                  <button onClick={() => review(subscription.id, "reject")} className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-black"><X className="h-4 w-4" /> Reject</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
