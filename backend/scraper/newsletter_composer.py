"""Shared Reddit-to-newsletter composition pipeline."""

import logging
import hashlib
from typing import Dict, List, Optional

from .chatgpt_client import ChatGPTClient
from .reddit_scraper import RedditScraper

logger = logging.getLogger(__name__)


class NewsletterComposer:
    """Fetch once, enrich once, then reuse the resulting content package."""

    def __init__(
        self,
        config,
        reddit_scraper: Optional[RedditScraper] = None,
        chatgpt_client: Optional[ChatGPTClient] = None,
    ):
        self.config = config
        self.reddit = reddit_scraper or RedditScraper(config)
        self.chatgpt = chatgpt_client or ChatGPTClient(config)

    @staticmethod
    def fallback_teaser(title: str) -> str:
        clean_title = " ".join(title.split()).rstrip(".?!")
        if len(clean_title) > 105:
            clean_title = clean_title[:102].rsplit(" ", 1)[0] + "…"
        frames = [
            "The history book skipped the weird part. Reddit, predictably, did not.",
            "A small fact with an unnecessarily large invitation to procrastinate.",
            "The headline sounds settled. The comments have requested a recount.",
            "One detail turns a simple fact into a very respectable rabbit hole.",
            "Useful knowledge, assuming trivia night ever becomes a survival situation.",
            "The internet found the footnote and immediately made it the main event.",
        ]
        digest = hashlib.sha256(clean_title.encode("utf-8")).digest()[0]
        return f"{clean_title}. {frames[digest % len(frames)]}"

    def compose(
        self,
        subreddit: str,
        limit: int = 4,
        time_filter: str = "week",
        use_ai: bool = True,
    ) -> Dict:
        subreddit = subreddit.strip().lstrip("r/")
        posts = self.reddit.fetch_top_posts(subreddit, limit, time_filter)
        if not posts:
            raise ValueError(f"No posts returned for r/{subreddit}")

        return self.enrich_posts(posts, subreddit, time_filter, use_ai)

    def enrich_posts(
        self,
        posts: List[Dict],
        subreddit: str = "mixed",
        time_filter: str = "week",
        use_ai: bool = True,
    ) -> Dict:
        """Enrich posts already fetched by the legacy scheduled job."""

        ai_available = use_ai
        ai_success_count = 0
        warnings = []
        for post in posts:
            post["trend_label"] = f"{post.get('score', 0):,} community points"
            summary = post.get("gpt_summary", "")
            comment_summary = post.get("comment_summary", "")
            if ai_available:
                summary = self.chatgpt.summarize_and_analyze(
                    post["title"], post.get("selftext", "")
                )
                if summary.startswith("[") and "失败" in summary:
                    warnings.append(summary)
                    ai_available = False
                    teaser = self.fallback_teaser(post["title"])
                elif post.get("top_comments"):
                    comment_summary = self.chatgpt.summarize_comments(post["top_comments"])
                    teaser = self.chatgpt.generate_newsletter_teaser(
                        post["title"], summary, comment_summary
                    )
                    if teaser.startswith("[") and "失败" in teaser:
                        warnings.append(teaser)
                        ai_available = False
                        teaser = self.fallback_teaser(post["title"])
                    else:
                        ai_success_count += 1
                else:
                    teaser = self.chatgpt.generate_newsletter_teaser(
                        post["title"], summary, comment_summary
                    )
                    if teaser.startswith("[") and "失败" in teaser:
                        warnings.append(teaser)
                        ai_available = False
                        teaser = self.fallback_teaser(post["title"])
                    else:
                        ai_success_count += 1
            else:
                teaser = self.fallback_teaser(post["title"])

            post["gpt_summary"] = summary
            post["comment_summary"] = comment_summary
            post["newsletter_teaser"] = teaser

        if ai_available and use_ai and self.config.get_enable_editor_summary():
            editor_words = self.chatgpt.generate_editor_words(posts)
            if editor_words.startswith("[") and "失败" in editor_words:
                warnings.append(editor_words)
                editor_words = self._fallback_editor_words(subreddit)
        else:
            editor_words = self._fallback_editor_words(subreddit)

        return {
            "subreddit": subreddit,
            "time_filter": time_filter,
            "posts": posts,
            "editor_words": editor_words,
            "uses_ai": ai_success_count == len(posts),
            "generation_mode": (
                "ai" if ai_success_count == len(posts) else "mixed" if ai_success_count else "fallback"
            ),
            "generation_warnings": warnings,
        }

    @staticmethod
    def _fallback_editor_words(subreddit: str) -> str:
        return (
            f"This week's r/{subreddit} rabbit holes, trimmed to the useful bits. "
            "Reddit did the arguing; you get the curious part."
        )
