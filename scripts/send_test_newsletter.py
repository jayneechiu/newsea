#!/usr/bin/env python3
"""Render and send a Newsea test newsletter using local preview cards."""

import argparse
import json
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.scraper.config_manager import ConfigManager
from backend.scraper.newsletter_sender import NewsletterSender


def load_preview_posts(limit: int) -> list[dict]:
    cards_path = REPOSITORY_ROOT / "ui" / "src" / "data" / "demo-cards.json"
    cards = json.loads(cards_path.read_text(encoding="utf-8"))
    posts = []

    for index, card in enumerate(cards[:limit], start=1):
        source = card.get("sources", [{}])[0]
        source_url = source.get("url", "https://www.reddit.com/")
        audience = card.get("audience", "Reddit communities")
        subreddit = source.get("label", audience).removeprefix("r/").replace(" ", "")
        posts.append(
            {
                "id": card["id"],
                "title": card["headline"],
                "subreddit": subreddit,
                "author": "Newsea signal desk",
                "score": card.get("sourceCount", 0),
                "num_comments": card.get("communityCount", 0),
                "permalink": source_url,
                "url": source_url,
                "selftext": card.get("context", ""),
                "gpt_summary": card.get("context", ""),
                "newsletter_teaser": card.get("emailTeaser", card.get("context", "")),
                "trend_label": card.get("trendLabel", "Community signal"),
                "comment_summary": "",
                "takeaways": card.get("takeaways", []),
                "display_order": index,
            }
        )

    return posts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=4, help="Number of preview signals to include")
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Write HTML to /tmp/newsea-test-newsletter.html without sending email",
    )
    parser.add_argument(
        "--html-file",
        type=Path,
        help="Send an already-rendered HTML file without fetching or regenerating content",
    )
    parser.add_argument(
        "--package-file",
        type=Path,
        help="Render and send an existing newsletter JSON package without Reddit or OpenAI calls",
    )
    args = parser.parse_args()

    config = ConfigManager(str(REPOSITORY_ROOT / ".env"))
    sender = NewsletterSender(config)

    if args.package_file:
        package_path = args.package_file.expanduser().resolve()
        if not package_path.is_file():
            print(f"Newsletter package not found: {package_path}", file=sys.stderr)
            return 1
        package = json.loads(package_path.read_text(encoding="utf-8"))
        recipients = config.get_recipients()
        print(f"Sending saved newsletter package to {len(recipients)} configured recipient(s)...")
        success, _ = sender.send_newsletter(
            package["posts"], package.get("editor_words"), recipients=recipients
        )
        if not success:
            print("Saved newsletter package could not be sent.", file=sys.stderr)
            return 1
        print("Saved newsletter package sent successfully. No Reddit or OpenAI request was made.")
        return 0

    if args.html_file:
        html_path = args.html_file.expanduser().resolve()
        if not html_path.is_file():
            print(f"Rendered newsletter not found: {html_path}", file=sys.stderr)
            return 1
        recipients = config.get_recipients()
        from_email = config.get_smtp_from_email()
        if not recipients or not from_email:
            print("SMTP sender and at least one test recipient are required.", file=sys.stderr)
            return 1
        message = MIMEMultipart("alternative")
        message["Subject"] = sender._generate_subject()
        message["From"] = formataddr(("Newsea", from_email))
        message["To"] = formataddr(("Newsea reader", from_email))
        message.attach(
            MIMEText(
                "This Newsea test email was rendered from previously fetched Reddit data. "
                "Open the HTML version to view the full preview.",
                "plain",
                "utf-8",
            )
        )
        message.attach(MIMEText(html_path.read_text(encoding="utf-8"), "html", "utf-8"))
        print(f"Sending existing rendered newsletter to {len(recipients)} configured recipient(s)...")
        if not sender._send_email(message, recipients):
            print("Rendered newsletter could not be sent.", file=sys.stderr)
            return 1
        print("Rendered newsletter sent successfully. No Reddit or OpenAI request was made.")
        return 0

    posts = load_preview_posts(max(1, min(args.limit, 8)))
    editor_words = (
        "Four conversations worth carrying into next week—compressed into the useful conclusion, "
        "the strongest community insight, and a path back to the source."
    )

    if args.render_only:
        output_path = Path("/tmp/newsea-test-newsletter.html")
        output_path.write_text(sender._generate_newsletter_html(posts, editor_words), encoding="utf-8")
        print(f"Rendered {len(posts)} signals to {output_path}")
        return 0

    recipients = config.get_recipients()
    print(f"Sending Newsea test newsletter to {len(recipients)} configured recipient(s)...")
    success, _ = sender.send_newsletter(posts, editor_words)
    if not success:
        print("Test newsletter could not be sent.", file=sys.stderr)
        return 1

    print("Test newsletter sent successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
