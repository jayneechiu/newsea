"""Tests for the shared newsletter composition pipeline."""

import unittest

from backend.scraper.newsletter_composer import NewsletterComposer


class FakeConfig:
    def get_enable_editor_summary(self):
        return True


class FakeReddit:
    def fetch_top_posts(self, subreddit, limit, time_filter):
        return [
            {
                "id": "one",
                "title": "Why humans sleep less than other primates",
                "subreddit": subreddit,
                "score": 42,
                "selftext": "",
                "top_comments": [],
            },
            {
                "id": "two",
                "title": "How Canada's two-dollar coin got its nickname",
                "subreddit": subreddit,
                "score": 38,
                "selftext": "",
                "top_comments": [],
            },
        ]


class FakeGPT:
    def summarize_and_analyze(self, title, content):
        return f"Summary: {title}"

    def summarize_comments(self, comments):
        return "Community summary"

    def generate_newsletter_teaser(self, title, summary, comment_summary):
        return f"A curious hook about {title.lower()}."

    def generate_editor_words(self, posts):
        return "Two rabbit holes, one inbox, and no obligation to read the entire internet."


class NewsletterComposerTests(unittest.TestCase):
    def test_ai_content_is_prepared_once_as_a_reusable_package(self):
        composer = NewsletterComposer(FakeConfig(), FakeReddit(), FakeGPT())

        package = composer.compose("todayilearned", 2, "week", use_ai=True)

        self.assertTrue(package["uses_ai"])
        self.assertEqual(len(package["posts"]), 2)
        self.assertNotEqual(
            package["posts"][0]["newsletter_teaser"],
            package["posts"][1]["newsletter_teaser"],
        )
        self.assertIn("Two rabbit holes", package["editor_words"])

    def test_non_ai_fallback_is_specific_to_each_title(self):
        composer = NewsletterComposer(FakeConfig(), FakeReddit(), FakeGPT())

        package = composer.compose("todayilearned", 2, "week", use_ai=False)

        teasers = [post["newsletter_teaser"] for post in package["posts"]]
        self.assertEqual(len(set(teasers)), 2)
        self.assertNotIn("Reddit has opinions, naturally", " ".join(teasers))


if __name__ == "__main__":
    unittest.main()
