#!/usr/bin/env python3
"""Fetch real Reddit posts and render a local Newsea newsletter without sending it."""

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.scraper.config_manager import ConfigManager
from backend.scraper.newsletter_composer import NewsletterComposer
from backend.scraper.newsletter_sender import NewsletterSender
from backend.scraper.reddit_scraper import RedditScraper


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subreddit", default="todayilearned")
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--time-filter", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    parser.add_argument("--without-ai", action="store_true", help="Skip OpenAI and use title-specific fallback teasers")
    parser.add_argument("--output", default="/tmp/newsea-live-newsletter.html")
    parser.add_argument("--package-output", default="/tmp/newsea-live-newsletter.json")
    parser.add_argument("--from-package", type=Path, help="Render an existing package without Reddit or OpenAI calls")
    parser.add_argument("--refresh-fallbacks", action="store_true", help="Replace teasers in a saved package with current offline fallbacks")
    args = parser.parse_args()

    config = ConfigManager(str(REPOSITORY_ROOT / ".env"))
    subreddit = args.subreddit.strip().lstrip("r/")
    if args.from_package:
        package = json.loads(args.from_package.expanduser().read_text(encoding="utf-8"))
        print(f"Reusing content package {args.from_package}; no Reddit or OpenAI request was made.")
        if args.refresh_fallbacks:
            for post in package["posts"]:
                post["newsletter_teaser"] = NewsletterComposer.fallback_teaser(post["title"])
            package["editor_words"] = NewsletterComposer._fallback_editor_words(package["subreddit"])
            package["uses_ai"] = False
            package["generation_mode"] = "fallback"
            package_path = Path(args.package_output).expanduser().resolve()
            package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved refreshed fallback package to {package_path}")
    else:
        scraper = RedditScraper(config)
        composer = NewsletterComposer(config, reddit_scraper=scraper)
        package = composer.compose(
            subreddit,
            max(1, min(args.limit, 8)),
            args.time_filter,
            use_ai=not args.without_ai,
        )
        package_path = Path(args.package_output).expanduser().resolve()
        package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved reusable content package to {package_path}")

    posts = package["posts"]

    sender = NewsletterSender(config)
    output_path = Path(args.output).expanduser().resolve()
    output_path.write_text(
        sender._generate_newsletter_html(
            posts,
            package["editor_words"],
        ),
        encoding="utf-8",
    )
    print(f"Rendered {len(posts)} real Reddit posts to {output_path}")
    for post in posts:
        print(f"- {post['title']} ({post['permalink']})")
    print("No email was sent. Reuse the JSON package to preview or send this exact edition.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
