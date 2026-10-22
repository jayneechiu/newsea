"""Build the static live-cards.json snapshot served by the GitHub Pages demo.

Usage:
    python -m backend.scraper.build_live_snapshot --out ui/public/live/live-cards.json

Needs REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET (read-only app auth is enough).
OPENAI_API_KEY is optional: without it cards fall back to raw post text and top comments.
"""

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from backend.api.feed_cards import MAX_TAKEAWAYS, _compact_number, post_to_card

logger = logging.getLogger(__name__)

LOCALIZE_PROMPT = """You write cards for Newsea, a visual digest of useful Reddit conversations.

Post title: {title}
Post text: {selftext}
Top comments:
{comments}

Return only a JSON object with these keys:
"context_en": one English teaser sentence (16-28 words), curious but accurate, light dry humor only if it fits.
"takeaways_en": 2-3 short English insights distilled from the comments (max 25 words each).
"headline_zh": the title translated into natural Simplified Chinese.
"context_zh": the teaser in natural Simplified Chinese.
"takeaways_zh": the takeaways in natural Simplified Chinese, same order.
Do not invent facts, numbers, quotes or identities. No Markdown or emoji."""


def _parse_json(text: str) -> Optional[Dict]:
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    keys = ("context_en", "takeaways_en", "headline_zh", "context_zh", "takeaways_zh")
    if not all(data.get(key) for key in keys):
        return None
    if not isinstance(data["takeaways_en"], list) or not isinstance(data["takeaways_zh"], list):
        return None
    return data


def localize_post(post: Dict, call_gpt) -> Optional[Dict]:
    """One model call returns English + Chinese copy; None means use the raw fallback."""
    comments = "\n".join(f"- {c.get('body', '')[:200]}" for c in (post.get("top_comments") or [])[:5])
    prompt = LOCALIZE_PROMPT.format(
        title=post["title"], selftext=(post.get("selftext") or "")[:500], comments=comments or "(none)"
    )
    return _parse_json(call_gpt(prompt, max_tokens=700))


def build_live_card(post: Dict, ai: Optional[Dict]) -> Dict:
    card = post_to_card(post)
    upvotes = _compact_number(int(post.get("score") or 0))
    if ai:
        card["context"] = ai["context_en"]
        card["takeaways"] = [str(t) for t in ai["takeaways_en"][:MAX_TAKEAWAYS]]
        card["i18n"] = {
            "zh": {
                "headline": ai["headline_zh"],
                "context": ai["context_zh"],
                "takeaways": [str(t) for t in ai["takeaways_zh"][:MAX_TAKEAWAYS]],
                "trendLabel": f"{upvotes} 赞",
            }
        }
    else:
        card["i18n"] = {"zh": {"trendLabel": f"{upvotes} 赞"}}
    return card


def _round_robin_by_subreddit(posts: List[Dict]) -> List[Dict]:
    """Highest-scoring post of each subreddit first, so small communities still show up."""
    groups: Dict[str, List[Dict]] = {}
    for post in sorted(posts, key=lambda p: p.get("score") or 0, reverse=True):
        groups.setdefault((post.get("subreddit") or "").lower(), []).append(post)
    ordered, queues = [], list(groups.values())
    while queues:
        ordered.extend(queue.pop(0) for queue in queues)
        queues = [queue for queue in queues if queue]
    return ordered


def build_snapshot(posts: List[Dict], call_gpt=None, limit: int = 12) -> Dict:
    cards, seen = [], set()
    for post in _round_robin_by_subreddit(posts):
        if not post.get("id") or not post.get("title") or post.get("over_18") or post["id"] in seen:
            continue
        seen.add(post["id"])
        cards.append(build_live_card(post, localize_post(post, call_gpt) if call_gpt else None))
        if len(cards) >= limit:
            break
    return {"updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cards": cards}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="ui/public/live/live-cards.json")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # The scraper's own GPT summaries are Chinese-only; the snapshot does its own bilingual call.
    os.environ["ENABLE_GPT_SUMMARIES"] = "false"
    os.environ["NEWSLETTER_POSTS_LIMIT"] = str(args.limit * 3)
    from backend.scraper.config_manager import ConfigManager
    from backend.scraper.reddit_scraper import RedditScraper

    config = ConfigManager()
    posts = RedditScraper(config).get_hot_posts()
    call_gpt = None
    if config.get_chatgpt_api_key():
        from backend.scraper.chatgpt_client import ChatGPTClient

        call_gpt = ChatGPTClient(config)._call_gpt
    snapshot = build_snapshot(posts, call_gpt, args.limit)
    if not snapshot["cards"]:
        logger.error("No cards built; keeping the previous snapshot.")
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    translated = sum(1 for card in snapshot["cards"] if "headline" in card["i18n"]["zh"])
    logger.info("Wrote %d cards (%d bilingual) to %s", len(snapshot["cards"]), translated, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
