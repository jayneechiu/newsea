"""Tests for the static live-cards snapshot used by the Pages demo."""

import json
import unittest

from backend.scraper.build_live_snapshot import build_snapshot, localize_post


def make_post(post_id, score=100, **extra):
    post = {
        "id": post_id,
        "title": f"Title {post_id}",
        "subreddit": "AskReddit",
        "score": score,
        "selftext": "",
        "permalink": f"https://reddit.com/r/AskReddit/comments/{post_id}",
        "top_comments": [{"author": "a", "body": "Useful comment", "score": 5}],
    }
    post.update(extra)
    return post


AI_REPLY = json.dumps(
    {
        "context_en": "English teaser",
        "takeaways_en": ["one", "two", "three", "four"],
        "headline_zh": "中文标题",
        "context_zh": "中文导语",
        "takeaways_zh": ["一", "二", "三", "四"],
    },
    ensure_ascii=False,
)


class BuildSnapshotTests(unittest.TestCase):
    def test_bilingual_card_from_ai_reply(self):
        snapshot = build_snapshot([make_post("a", score=4100)], lambda prompt, max_tokens: AI_REPLY)
        card = snapshot["cards"][0]
        self.assertEqual(card["context"], "English teaser")
        self.assertEqual(card["takeaways"], ["one", "two", "three"])
        self.assertEqual(card["i18n"]["zh"]["headline"], "中文标题")
        self.assertEqual(card["i18n"]["zh"]["trendLabel"], "4.1K 赞")
        self.assertIn("updatedAt", snapshot)

    def test_bad_ai_reply_falls_back_to_raw_post(self):
        snapshot = build_snapshot([make_post("a")], lambda prompt, max_tokens: "[ChatGPT分析失败: HTTP错误 429]")
        card = snapshot["cards"][0]
        self.assertEqual(card["takeaways"], ["Useful comment"])
        self.assertNotIn("headline", card["i18n"]["zh"])

    def test_no_ai_skips_model_and_filters_nsfw_and_duplicates(self):
        posts = [make_post("a", score=1), make_post("b", score=9, over_18=True), make_post("a"), make_post("c", score=5)]
        cards = build_snapshot(posts, None, limit=10)["cards"]
        self.assertEqual([card["id"] for card in cards], ["reddit-a", "reddit-c"])

    def test_round_robin_keeps_small_subreddits(self):
        posts = [make_post("a", 900), make_post("b", 800), make_post("d", 3, subreddit="Dallas")]
        cards = build_snapshot(posts, None, limit=2)["cards"]
        self.assertEqual([card["id"] for card in cards], ["reddit-a", "reddit-d"])

    def test_localize_parses_fenced_json(self):
        reply = f"```json\n{AI_REPLY}\n```"
        self.assertEqual(localize_post(make_post("a"), lambda p, max_tokens: reply)["context_zh"], "中文导语")


if __name__ == "__main__":
    unittest.main()
