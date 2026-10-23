import { useState } from "react";
import { ArrowDown, ArrowUp, GripVertical, Plus, X } from "lucide-react";
import { useI18n, type MessageKey } from "@/i18n";
import { readInterestTags, saveInterestTags } from "@/services/account";
import { STARTER_TAGS, type TagId } from "@/services/tags";

// eslint-disable-next-line react-refresh/only-export-components
export const tagLabels: Record<TagId, MessageKey> = {
  food: "tagFood",
  money: "tagMoney",
  career: "tagCareer",
  tech: "tagTech",
  travel: "tagTravel",
  style: "tagStyle",
  family: "tagFamily",
  culture: "tagCulture",
  dallas: "tagDallas",
  health: "tagHealth",
};

const iconButton = "rounded-full p-1.5 text-slate-400 transition hover:bg-[#f4f1e9] hover:text-slate-950 disabled:opacity-30";

/** Edits the signed-in reader's home tabs: their interest list, in display order. */
export default function TagPicker({ onDone }: { onDone: () => void }) {
  const { t } = useI18n();
  const [tabs, setTabs] = useState<TagId[]>(() => readInterestTags() ?? []);
  const [dragging, setDragging] = useState<number | null>(null);
  const available = STARTER_TAGS.map(({ id }) => id).filter((id) => !tabs.includes(id));

  const move = (from: number, to: number) =>
    setTabs((current) => {
      if (to < 0 || to >= current.length) return current;
      const next = [...current];
      next.splice(to, 0, ...next.splice(from, 1));
      return next;
    });

  return (
    <section className="mb-6 rounded-[2rem] border border-slate-950/10 bg-white p-6 sm:mb-10 sm:p-8" aria-labelledby="tab-editor-title">
      <h2 id="tab-editor-title" className="text-2xl font-black tracking-[-0.03em]">
        {t("editorTitle")}
      </h2>
      <p className="mt-2 max-w-2xl text-slate-500">{t("editorBody")}</p>

      <ol className="mt-5 max-w-md space-y-2">
        <li className="flex items-center gap-3 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-extrabold text-white">
          {t("tabHot")}
          <span className="ml-auto text-xs font-bold text-white/60">{t("editorPinned")}</span>
        </li>
        {tabs.map((id, index) => (
          <li
            key={id}
            draggable
            onDragStart={() => setDragging(index)}
            onDragOver={(event) => {
              event.preventDefault();
              if (dragging !== null && dragging !== index) {
                move(dragging, index);
                setDragging(index);
              }
            }}
            onDragEnd={() => setDragging(null)}
            className={`flex items-center gap-2 rounded-2xl border border-slate-950/10 bg-[#f4f1e9] px-3 py-2 text-sm font-extrabold ${
              dragging === index ? "opacity-50" : ""
            }`}
          >
            <GripVertical className="hidden h-4 w-4 cursor-grab text-slate-400 sm:block" aria-hidden="true" />
            <span className="flex-1">{t(tagLabels[id])}</span>
            <button type="button" className={iconButton} disabled={index === 0} onClick={() => move(index, index - 1)} aria-label={t("editorMoveUp", { tab: t(tagLabels[id]) })}>
              <ArrowUp className="h-4 w-4" />
            </button>
            <button type="button" className={iconButton} disabled={index === tabs.length - 1} onClick={() => move(index, index + 1)} aria-label={t("editorMoveDown", { tab: t(tagLabels[id]) })}>
              <ArrowDown className="h-4 w-4" />
            </button>
            <button type="button" className={iconButton} onClick={() => setTabs(tabs.filter((tag) => tag !== id))} aria-label={t("editorRemove", { tab: t(tagLabels[id]) })}>
              <X className="h-4 w-4" />
            </button>
          </li>
        ))}
      </ol>

      {available.length > 0 && (
        <>
          <h3 className="mt-6 text-xs font-black uppercase tracking-[0.12em] text-slate-500">{t("editorAdd")}</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {available.map((id) => (
              <button
                type="button"
                key={id}
                onClick={() => setTabs([...tabs, id])}
                className="inline-flex items-center gap-1 rounded-full bg-[#f4f1e9] px-4 py-2 text-sm font-extrabold text-slate-600 transition hover:text-slate-950"
              >
                <Plus className="h-3.5 w-3.5" />
                {t(tagLabels[id])}
              </button>
            ))}
          </div>
        </>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => {
            saveInterestTags(tabs);
            onDone();
          }}
          className="rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white"
        >
          {t("editorSave")}
        </button>
        <button type="button" onClick={onDone} className="rounded-full px-5 py-3 text-sm font-bold text-slate-500 hover:text-slate-950">
          {t("editorCancel")}
        </button>
      </div>
    </section>
  );
}
