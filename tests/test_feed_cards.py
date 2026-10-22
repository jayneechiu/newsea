"""Tests for mapping enriched Reddit posts to feed ContentCards."""

import unittest

from backend.api.feed_cards import build_feed, post_to_card


def make_post(post_id, subreddit="AskReddit", **extra):
    post = {
        "id": post_id,
        "title": f"Title {post_id}",
        "subreddit": subreddit,
        "score": 4123,
        "num_comments": 87,
        "permalink": f"https://reddit.com/r/{subreddit}/comments/{post_id}",
        "newsletter_teaser": "A sharp teaser.",
        "top_comments": [{"body": "First comment"}, {"body": "Second comment"}],
    }
    post.update(extra)
    return post


class FeedCardsTest(unittest.TestCase):
    def test_post_maps_to_content_card_shape(self):
        card = post_to_card(make_post("abc"))
        self.assertEqual(card["id"], "reddit-abc")
        self.assertEqual(card["eyebrow"], "r/AskReddit")
        self.assertEqual(card["context"], "A sharp teaser.")
        self.assertEqual(card["takeaways"], ["First comment", "Second comment"])
        self.assertEqual(card["trendLabel"], "4.1K upvotes")
        self.assertEqual(card["communityCount"], 1)
        self.assertEqual(card["sources"][0]["url"], "https://reddit.com/r/AskReddit/comments/abc")
        self.assertIn(card["theme"], {"coral", "ocean", "lime", "gold", "violet", "ink"})

    def test_lanes_split_dallas_from_other_worlds(self):
        drafts = [{"posts": [make_post("d1", subreddit="Dallas"), make_post("o1")]}]
        self.assertEqual([c["id"] for c in build_feed(drafts, "dallas", 10)], ["reddit-d1"])
        self.assertEqual([c["id"] for c in build_feed(drafts, "other-worlds", 10)], ["reddit-o1"])
        self.assertEqual(len(build_feed(drafts, "everyone", 10)), 2)

    def test_skips_nsfw_duplicates_and_respects_limit(self):
        drafts = [
            {"posts": [make_post("a"), make_post("nsfw", over_18=True)]},
            {"posts": [make_post("a"), make_post("b"), make_post("c")]},
        ]
        self.assertEqual([c["id"] for c in build_feed(drafts, "everyone", 2)], ["reddit-a", "reddit-b"])

    def test_falls_back_when_no_teaser_or_comments(self):
        card = post_to_card(make_post("x", newsletter_teaser="", top_comments=[], selftext=""))
        self.assertEqual(card["context"], "Title x")
        self.assertEqual(card["takeaways"], ["Title x"])


if __name__ == "__main__":
    unittest.main()
