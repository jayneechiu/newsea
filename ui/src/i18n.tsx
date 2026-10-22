import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { ContentCard } from "@/types/content";

export type Lang = "en" | "zh";

const en = {
  demoMode: "Demo mode",
  tagline: "human signal feed",
  previewData: "Preview data",
  newsletter: "Newsletter",
  digest: "Digest",
  refreshFeed: "Refresh feed",
  feedViews: "Feed views",
  switchLanguage: "切换到中文",
  laneLive: "Live from Reddit",
  laneLiveShort: "Live",
  laneForYou: "For you",
  laneEveryone: "Everyone",
  laneDallas: "Dallas",
  laneOtherWorlds: "Other worlds",
  laneOtherWorldsShort: "Worlds",
  heroBadge: "Signal over noise",
  heroLine1: "What people know,",
  heroLine2: "before it becomes obvious.",
  heroBody: "The best conversations across Reddit, compressed into useful signals. No bait, no detours, no endless thread hunting.",
  signalsCount: "{count} signals",
  liveUpdated: "Real Reddit snapshot · updated {date}",
  clearedTitle: "You cleared this view.",
  clearedBody: "Reset hidden cards to bring every signal back.",
  resetCards: "Reset cards",
  openSignal: "Open signal: {headline}",
  saveSignal: "Save signal",
  removeSaved: "Remove from saved",
  save: "Save",
  saved: "Saved",
  like: "Like",
  liked: "Liked",
  likeSignal: "Like signal",
  unlikeSignal: "Unlike signal",
  driftedTitle: "This signal drifted away.",
  driftedBody: "It may have expired from this session.",
  backToFeed: "Back to the feed",
  backToSignals: "Back to signals",
  lessLikeThis: "Less like this",
  communitiesSources: "{communities} communities · {sources} sources",
  whyItMatters: "Why it matters",
  communitiesSampled: "Communities sampled",
  filedUnder: "Filed under",
  keepExploring: "Keep exploring",
  sameCurrent: "Signals with the same current",
  liveFeed: "Live feed",
  nlBadge: "The original Newsea format",
  nlTitle1: "The signal,",
  nlTitle2: "delivered slowly.",
  nlIntro: "Newsea began as a Reddit newsletter. The visual feed is now the primary product, but the digest remains a useful way to revisit the week without another infinite scroll.",
  nlChapter: "A preserved product chapter · not a dead feature",
  nlPreviewEdition: "Preview edition",
  nlEditorSignal: "Editor's signal",
  nlHeadline: "Four conversations worth carrying into next week.",
  nlEditorFallback: "No timeline anxiety. Just enough context, a curious hook, and a path back to the original discussion.",
  nlOpenOriginal: "Open the original conversation.",
  nlSeeConversation: "See the conversation →",
  nlExplore: "Explore every signal",
  nlInvite: "Request an invite",
  nlInviteTitle: "A quiet digest, with a human at the door.",
  nlInviteBody: "Every request is reviewed by Newsea's owner. Applying does not add you to a mailing list yet.",
  nlAwaiting: "Awaiting approval",
  nlAwaitingBody: "Your request is saved. No newsletter will be sent until it is approved.",
  nlName: "Name",
  nlOptional: "(optional)",
  nlNamePlaceholder: "How should we greet you?",
  nlEmail: "Email",
  nlRequesting: "Requesting…",
  nlRequest: "Request approval",
  nlError: "Could not save the request. Please try again.",
  nlWhyKeep: "Why keep it?",
  nlWhyTitle: "One pipeline, two consumption speeds.",
  nlWhy1: "The feed drives discovery.",
  nlWhy2: "The digest supports reflection.",
  nlWhy3: "Both use the same ContentCards.",
  nlOwnerControls: "Local owner controls",
  nlOwnerBody: "Generate a GPT-written draft, inspect every hook, review subscribers, then send the exact saved edition.",
  nlOwnerDesk: "Open owner desk",
  nlSafety: "Public preview safety",
  nlSafetyBody: "Email sending is hidden in public builds. Owners can enable the connected controls locally with",
};

export type MessageKey = keyof typeof en;

const zh: Record<MessageKey, string> = {
  demoMode: "演示模式",
  tagline: "人类信号流",
  previewData: "预览数据",
  newsletter: "简报",
  digest: "简报",
  refreshFeed: "刷新",
  feedViews: "信息流视图",
  switchLanguage: "Switch to English",
  laneLive: "Reddit 实时",
  laneLiveShort: "实时",
  laneForYou: "为你推荐",
  laneEveryone: "全部",
  laneDallas: "达拉斯",
  laneOtherWorlds: "其他世界",
  laneOtherWorldsShort: "世界",
  heroBadge: "信号胜于噪音",
  heroLine1: "大家已经知道的事，",
  heroLine2: "在它变得显而易见之前。",
  heroBody: "把 Reddit 上最好的讨论压缩成有用的信号。没有标题党，没有绕路，不用再翻遍整串回复。",
  signalsCount: "{count} 条信号",
  liveUpdated: "真实 Reddit 快照 · 更新于 {date}",
  clearedTitle: "这个视图已经被你清空了。",
  clearedBody: "重置隐藏的卡片，找回所有信号。",
  resetCards: "重置卡片",
  openSignal: "打开信号：{headline}",
  saveSignal: "收藏信号",
  removeSaved: "取消收藏",
  save: "收藏",
  saved: "已收藏",
  like: "喜欢",
  liked: "已喜欢",
  likeSignal: "喜欢这条信号",
  unlikeSignal: "取消喜欢",
  driftedTitle: "这条信号漂走了。",
  driftedBody: "它可能已在本次会话中过期。",
  backToFeed: "返回信息流",
  backToSignals: "返回信号",
  lessLikeThis: "减少此类",
  communitiesSources: "{communities} 个社区 · {sources} 个来源",
  whyItMatters: "为什么重要",
  communitiesSampled: "采样社区",
  filedUnder: "归类于",
  keepExploring: "继续探索",
  sameCurrent: "同一洋流里的信号",
  liveFeed: "信息流",
  nlBadge: "Newsea 最初的形态",
  nlTitle1: "信号，",
  nlTitle2: "慢慢送达。",
  nlIntro: "Newsea 最早是一份 Reddit 简报。现在视觉信息流是主产品，但简报依然是不用无限滚动、回顾一周的好方式。",
  nlChapter: "保留的产品篇章 · 不是废弃功能",
  nlPreviewEdition: "预览版",
  nlEditorSignal: "编辑的话",
  nlHeadline: "四个值得带进下周的讨论。",
  nlEditorFallback: "没有时间线焦虑。刚好够的背景、一个好奇的钩子，以及回到原始讨论的路径。",
  nlOpenOriginal: "打开原始讨论。",
  nlSeeConversation: "查看讨论 →",
  nlExplore: "探索所有信号",
  nlInvite: "申请邀请",
  nlInviteTitle: "一份安静的简报，门口有人把关。",
  nlInviteBody: "每个申请都由 Newsea 负责人审核。提交申请并不会立刻把你加入邮件列表。",
  nlAwaiting: "等待审核",
  nlAwaitingBody: "申请已保存。审核通过前不会发送任何简报。",
  nlName: "名字",
  nlOptional: "（可选）",
  nlNamePlaceholder: "我们该怎么称呼你？",
  nlEmail: "邮箱",
  nlRequesting: "提交中…",
  nlRequest: "提交申请",
  nlError: "申请保存失败，请重试。",
  nlWhyKeep: "为什么保留？",
  nlWhyTitle: "一条管线，两种阅读速度。",
  nlWhy1: "信息流负责发现。",
  nlWhy2: "简报负责回顾。",
  nlWhy3: "两者使用同一套 ContentCard。",
  nlOwnerControls: "本地负责人控制台",
  nlOwnerBody: "生成 GPT 草稿，检查每个钩子，审核订阅者，然后发送保存的那一版。",
  nlOwnerDesk: "打开控制台",
  nlSafety: "公开预览安全",
  nlSafetyBody: "公开构建中隐藏了邮件发送。负责人可在本地开启连接的控制：",
};

const messages: Record<Lang, Record<MessageKey, string>> = { en, zh };
const LANG_KEY = "newsea:lang";

function readLang(): Lang {
  const stored = localStorage.getItem(LANG_KEY);
  if (stored === "en" || stored === "zh") return stored;
  return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}

interface I18nValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: MessageKey, vars?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readLang);
  const value = useMemo<I18nValue>(() => {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    return {
      lang,
      setLang: (next) => {
        localStorage.setItem(LANG_KEY, next);
        setLangState(next);
      },
      t: (key, vars) =>
        messages[lang][key].replace(/\{(\w+)\}/g, (match, name: string) => String(vars?.[name] ?? match)),
    };
  }, [lang]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useI18n(): I18nValue {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside LanguageProvider");
  return value;
}

/** Swap in a card's translated copy; untranslated fields keep the English original. */
// eslint-disable-next-line react-refresh/only-export-components
export function localizeCard(card: ContentCard, lang: Lang): ContentCard {
  const translated = lang === "en" ? undefined : card.i18n?.[lang];
  return translated ? { ...card, ...translated } : card;
}
