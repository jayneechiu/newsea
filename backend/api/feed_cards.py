"""Map enriched Reddit posts (stored in newsletter_drafts) to the UI ContentCard shape."""

import hashlib
from typing import Dict, Iterable, List

THEMES = ["coral", "ocean", "lime", "gold", "violet", "ink"]
LANES = {"for-you", "everyone", "dallas", "other-worlds"}
DALLAS_SUBREDDITS = {"dallas", "dfw", "fortworth", "plano", "frisco", "texas"}
MAX_TAKEAWAYS = 3
MAX_TAKEAWAY_CHARS = 180


def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _theme_for(post_id: str) -> str:
    return THEMES[int(hashlib.md5(post_id.encode()).hexdigest(), 16) % len(THEMES)]


def _compact_number(value: int) -> str:
    return f"{value / 1000:.1f}K".replace(".0K", "K") if value >= 1000 else str(value)


def post_to_card(post: Dict) -> Dict:
    subreddit = post.get("subreddit") or "reddit"
    is_dallas = subreddit.lower() in DALLAS_SUBREDDITS
    comments = [c.get("body", "") for c in post.get("top_comments") or [] if c.get("body")]
    takeaways = [_shorten(body, MAX_TAKEAWAY_CHARS) for body in comments[:MAX_TAKEAWAYS]]
    context = post.get("newsletter_teaser") or _shorten(post.get("selftext", ""), 240) or post["title"]
    url = post.get("permalink") or post.get("url") or f"https://reddit.com/r/{subreddit}"
    return {
        "id": f"reddit-{post['id']}",
        "lane": ["for-you", "everyone", "dallas" if is_dallas else "other-worlds"],
        "cardType": "local-trend" if is_dallas else "community-insight",
        "theme": _theme_for(str(post["id"])),
        "eyebrow": f"r/{subreddit}",
        "headline": post["title"],
        "context": context,
        "takeaways": takeaways or [context],
        "topics": [subreddit.lower()],
        "audience": "Everyone",
        "sourceCount": 1,
        "communityCount": 1,
        "trendLabel": f"{_compact_number(int(post.get('score') or 0))} upvotes",
        "sources":  [{"label": f"r/{subreddit} thread", "url": url}],
    }


def build_feed(drafts: Iterable[Dict], lane: str, limit: int) -> List[Dict]:
    """Newest drafts first; skip NSFW and duplicate posts."""
    cards, seen = [], set()
    for draft in drafts:
        for post in draft.get("posts") or []:
            if not post.get("id") or not post.get("title") or post.get("over_18") or post["id"] in seen:
                continue
            seen.add(post["id"])
            card = post_to_card(post)
            if lane in card["lane"]:
                cards.append(card)
            if len(cards) >= limit:
                return cards
    return cards
