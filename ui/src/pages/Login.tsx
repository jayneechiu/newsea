import { useState } from "react";
import { ArrowLeft, Bookmark, Lock, Mail, Sparkles, Waves, type LucideIcon } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import LanguageToggle from "@/components/LanguageToggle";
import { useI18n, type MessageKey } from "@/i18n";
import { login, register } from "@/services/account";
import { hasAccountBackend } from "@/services/api";
import { safeNextPath } from "@/services/redirect";

const perks: Array<{ icon: LucideIcon; title: MessageKey; body: MessageKey }> = [
  { icon: Sparkles, title: "authPerkFeedTitle", body: "authPerkFeedBody" },
  { icon: Bookmark, title: "authPerkSyncTitle", body: "authPerkSyncBody" },
  { icon: Mail, title: "authPerkDigestTitle", body: "authPerkDigestBody" },
];

function authErrorKey(error: unknown, isLogin: boolean): MessageKey {
  const status = (error as { response?: { status?: number } }).response?.status;
  if (status === 429) return "authErrorRateLimit";
  if (status === 422) return "authErrorInvalid";
  return isLogin ? "authErrorLogin" : "authErrorSignup";
}

const field =
  "w-full rounded-2xl border border-slate-950/15 bg-[#f4f1e9] py-3.5 pl-11 pr-4 text-sm font-semibold outline-none transition placeholder:text-slate-400 focus:border-slate-950 focus:bg-white";

function Login() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const next = safeNextPath(searchParams.get("next"));
  const [isLogin, setIsLogin] = useState(searchParams.get("mode") !== "signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<MessageKey | null>(null);

  const switchMode = (loginTab: boolean) => {
    setIsLogin(loginTab);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    if (hasAccountBackend) {
      setError(null);
      try {
        await (isLogin ? login : register)(email, password);
        navigate(next, { replace: true });
      } catch (err) {
        setError(authErrorKey(err, isLogin));
      } finally {
        setLoading(false);
      }
      return;
    }

    // 模拟登录
    setTimeout(() => {
      localStorage.setItem("userEmail", email);
      localStorage.setItem("isLoggedIn", "true");
      setLoading(false);
      navigate(next, { replace: true });
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-[#f4f1e9] text-slate-950">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5" aria-label={t("authBrowse")}>
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-white shadow-lg shadow-slate-950/15">
            <Waves className="h-5 w-5" />
          </span>
          <div>
            <div className="text-lg font-black leading-none tracking-[-0.04em]">newsea</div>
            <div className="mt-1 text-[9px] font-black uppercase tracking-[0.22em] text-slate-500">{t("tagline")}</div>
          </div>
        </Link>
        <LanguageToggle />
      </header>

      <main className="mx-auto grid max-w-6xl gap-8 px-4 pb-16 pt-4 sm:px-6 lg:grid-cols-[1fr_440px] lg:items-center lg:gap-16 lg:pt-12">
        <section className="order-2 lg:order-1">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#dfff55] px-3 py-1.5 text-[11px] font-black uppercase tracking-[0.15em]">
            <Sparkles className="h-3.5 w-3.5" />
            {t("authBadge")}
          </div>
          <h1 className="max-w-xl text-4xl font-black leading-[0.95] tracking-[-0.055em] sm:text-5xl lg:text-6xl">
            {t("authHeadline")}
          </h1>
          <ul className="mt-8 grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
            {perks.map(({ icon: Icon, title, body }) => (
              <li key={title} className="flex gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white shadow-sm">
                  <Icon className="h-4 w-4" />
                </span>
                <div>
                  <div className="font-black">{t(title)}</div>
                  <p className="mt-0.5 text-sm font-semibold leading-6 text-slate-500">{t(body)}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="order-1 rounded-[2rem] bg-white p-6 shadow-2xl shadow-slate-950/10 sm:p-8 lg:order-2">
          <div className="grid grid-cols-2 gap-1 rounded-full bg-[#f4f1e9] p-1">
            {[true, false].map((loginTab) => (
              <button
                key={String(loginTab)}
                type="button"
                aria-pressed={isLogin === loginTab}
                onClick={() => switchMode(loginTab)}
                className={`rounded-full py-2.5 text-sm font-extrabold transition ${
                  isLogin === loginTab ? "bg-slate-950 text-white shadow" : "text-slate-500 hover:text-slate-950"
                }`}
              >
                {t(loginTab ? "authLogIn" : "authSignUp")}
              </button>
            ))}
          </div>

          <h2 className="mt-6 text-2xl font-black tracking-[-0.03em]">
            {t(isLogin ? "authWelcomeBack" : "authCreateTitle")}
          </h2>
          <p className="mt-1 text-sm font-semibold text-slate-500">
            {t(isLogin ? "authWelcomeBackBody" : "authCreateBody")}
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="mb-1.5 block text-xs font-black uppercase tracking-[0.12em] text-slate-500">{t("authEmail")}</span>
              <span className="relative block">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                  className={field}
                  required
                />
              </span>
            </label>

            {(isLogin || hasAccountBackend) && (
              <label className="block">
                <span className="mb-1.5 block text-xs font-black uppercase tracking-[0.12em] text-slate-500">{t("authPassword")}</span>
                <span className="relative block">
                  <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    minLength={hasAccountBackend && !isLogin ? 8 : undefined}
                    autoComplete={isLogin ? "current-password" : "new-password"}
                    className={field}
                    required
                  />
                </span>
                {!isLogin && <span className="mt-1.5 block text-xs font-semibold text-slate-400">{t("authPasswordHint")}</span>}
              </label>
            )}

            {error && (
              <p role="alert" className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-red-700">
                {t(error)}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-full bg-slate-950 py-3.5 text-sm font-bold text-white transition hover:bg-slate-800 disabled:opacity-50"
            >
              {loading ? t("authWorking") : t(isLogin ? "authLogIn" : "authCreateAccount")}
            </button>
          </form>

          {!hasAccountBackend && (
            <p className="mt-4 rounded-2xl bg-amber-100 px-4 py-3 text-center text-xs font-bold text-amber-950">{t("authDemoHint")}</p>
          )}

          <Link
            to="/"
            className="mt-6 flex items-center justify-center gap-1.5 text-sm font-bold text-slate-500 transition hover:text-slate-950"
          >
            <ArrowLeft className="h-4 w-4" />
            {t("authBrowse")}
          </Link>
        </section>
      </main>
    </div>
  );
}

export default Login;
