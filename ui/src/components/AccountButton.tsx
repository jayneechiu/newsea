import { LogIn, LogOut } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useI18n } from "@/i18n";
import { logout } from "@/services/account";
import { loginPath } from "@/services/redirect";

const pill =
  "inline-flex h-10 items-center gap-1.5 rounded-full border border-slate-950/15 bg-white px-3 text-xs font-extrabold transition hover:bg-slate-950 hover:text-white";

export default function AccountButton() {
  const { t } = useI18n();
  const location = useLocation();
  const email = localStorage.getItem("isLoggedIn") === "true" ? localStorage.getItem("userEmail") ?? "" : null;

  if (email === null) {
    return (
      <Link to={loginPath(location.pathname + location.search)} className={pill}>
        <LogIn className="h-4 w-4" />
        {t("signInOrUp")}
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="hidden max-w-[12rem] truncate text-xs font-bold text-slate-600 md:inline" title={email}>
        {email}
      </span>
      <button
        type="button"
        onClick={async () => {
          await logout();
          // Reload so every page drops the signed-out account's likes, saves and interests.
          window.location.reload();
        }}
        className={pill}
      >
        <LogOut className="h-4 w-4" />
        {t("logOut")}
      </button>
    </div>
  );
}
