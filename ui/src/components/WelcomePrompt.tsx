import { useEffect, useRef, useState } from "react";
import { Sparkles, X } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { tagLabels } from "@/components/TagPicker";
import { useI18n } from "@/i18n";
import { readInterestTags, saveInterestTags } from "@/services/account";
import { loginPath } from "@/services/redirect";
import { STARTER_TAGS, type TagId } from "@/services/tags";

const SEEN_KEY = "newsea:welcome-seen";
const DELAY_MS = 3000;

/** A one-time, dismissible invite for guests: browse first, personalize after a few seconds. */
export default function WelcomePrompt() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [selected, setSelected] = useState<TagId[]>(() => readInterestTags() ?? []);

  useEffect(() => {
    if (localStorage.getItem("isLoggedIn") === "true" || localStorage.getItem(SEEN_KEY)) return;
    const timer = window.setTimeout(() => {
      dialogRef.current?.showModal();
      localStorage.setItem(SEEN_KEY, "1");
    }, DELAY_MS);
    return () => window.clearTimeout(timer);
  }, []);

  const close = () => dialogRef.current?.close();
  const toggle = (id: TagId) =>
    setSelected((current) => (current.includes(id) ? current.filter((tag) => tag !== id) : [...current, id]));
  const keepInterests = () => {
    if (selected.length) saveInterestTags(selected);
  };

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="welcome-title"
      onClick={(event) => event.target === dialogRef.current && close()}
      className="m-auto max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-lg overflow-y-auto rounded-[2rem] bg-white p-0 text-slate-950 shadow-2xl backdrop:bg-slate-950/40 backdrop:backdrop-blur-sm"
    >
      <div className="p-6 sm:p-8">
        <div className="flex items-start justify-between gap-4">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#dfff55] px-3 py-1.5 text-[11px] font-black uppercase tracking-[0.15em]">
            <Sparkles className="h-3.5 w-3.5" />
            {t("welcomeBadge")}
          </div>
          <button type="button" onClick={close} aria-label={t("welcomeLater")} className="rounded-full p-1 text-slate-400 hover:text-slate-950">
            <X className="h-5 w-5" />
          </button>
        </div>
        <h2 id="welcome-title" className="mt-4 text-2xl font-black tracking-[-0.03em]">
          {t("welcomeTitle")}
        </h2>
        <p className="mt-2 text-slate-500">{t("welcomeBody")}</p>

        <div className="mt-5 flex flex-wrap gap-2">
          {STARTER_TAGS.map(({ id }) => {
            const active = selected.includes(id);
            return (
              <button
                type="button"
                key={id}
                aria-pressed={active}
                onClick={() => toggle(id)}
                className={`rounded-full px-4 py-2 text-sm font-extrabold transition ${
                  active ? "bg-slate-950 text-white" : "bg-[#f4f1e9] text-slate-600 hover:text-slate-950"
                }`}
              >
                {t(tagLabels[id])}
              </button>
            );
          })}
        </div>

        <div className="mt-6">
          <button
            type="button"
            onClick={() => {
              keepInterests();
              close();
              navigate(loginPath("/", "signup"));
            }}
            className="w-full rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white"
          >
            {t("welcomeCreate")}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm">
          <Link to={loginPath("/")} onClick={() => { keepInterests(); close(); }} className="font-bold text-slate-950 underline-offset-4 hover:underline">
            {t("welcomeHaveAccount")}
          </Link>
          <button type="button" onClick={close} className="font-bold text-slate-500 hover:text-slate-950">
            {t("welcomeLater")}
          </button>
        </div>
      </div>
    </dialog>
  );
}
