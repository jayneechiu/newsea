import { Languages } from "lucide-react";
import { useI18n } from "@/i18n";

export default function LanguageToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <button
      type="button"
      onClick={() => setLang(lang === "en" ? "zh" : "en")}
      className="inline-flex h-10 items-center gap-1.5 rounded-full border border-slate-950/15 bg-white px-3 text-xs font-extrabold transition hover:bg-slate-950 hover:text-white"
      aria-label={t("switchLanguage")}
      title={t("switchLanguage")}
    >
      <Languages className="h-4 w-4" />
      {lang === "en" ? "中文" : "EN"}
    </button>
  );
}
