#!/usr/bin/env python3
"""
Standalone scraper job entry point (moved to app/backend/scraper)
Usage: python app/backend/scraper/run_job.py [--test]
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.scraper.config_manager import ConfigManager
from backend.scraper.reddit_scraper import RedditScraper
from backend.scraper.chatgpt_client import ChatGPTClient
from backend.scraper.newsletter_sender import NewsletterSender
from backend.scraper.newsletter_composer import NewsletterComposer
from backend.scraper.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)


def run_scraper_job(test_mode=False, force_resend=False):
    start_time = datetime.now()
    logger.info("=== Starting scraper job ===")
    try:
        logger.info("Initializing services...")
        config = ConfigManager()
        reddit = RedditScraper(config)
        chatgpt = ChatGPTClient(config)
        sender = NewsletterSender(config)
        composer = NewsletterComposer(config, reddit, chatgpt)
        db = DatabaseManager()
        logger.info("All services initialized successfully")
        if test_mode:
            logger.info("Testing connections...")
            test_posts = reddit.get_hot_posts(limit=1)
            logger.info(f"✓ Reddit OK ({len(test_posts)} posts)")
            if db.test_connection():
                logger.info("✓ Database OK")
            logger.info("All connections successful!")
            return
        logger.info("Fetching hot posts from Reddit...")
        posts_limit = config.get_posts_limit()
        posts = reddit.get_hot_posts(limit=posts_limit)
        logger.info(f"Fetched {len(posts)} posts from Reddit")
        newsletter_limit = config.get_newsletter_posts_limit()
        if force_resend:
            logger.info("Force resend enabled: skipping V2 new-post filter")
            selected_posts = posts[:newsletter_limit]
        else:
            logger.info("[V2] Filtering new posts using reddit_posts...")
            new_posts = db.filter_new_posts_v2(posts)
            logger.info(f"Found {len(new_posts)} new posts")
            if not new_posts:
                logger.info("No new posts to send")
                return
            selected_posts = new_posts[:newsletter_limit]
        logger.info(f"Selected {len(selected_posts)} posts for newsletter")
        logger.info("Composing reusable newsletter content package...")
        package = composer.enrich_posts(
            selected_posts,
            subreddit="mixed",
            time_filter="day",
            use_ai=config.get_enable_gpt_summaries(),
        )
        selected_posts = package["posts"]
        editor_words = package["editor_words"]
        draft = db.create_newsletter_draft(package)
        logger.info("Sending newsletter...")
        recipients = db.get_approved_newsletter_recipients()
        if not recipients:
            logger.info("No approved recipients; saved draft without sending")
            return
        db.update_newsletter_draft_status(draft["id"], "sending")
        success, _ = sender.send_newsletter(selected_posts, editor_words, recipients=recipients)
        db.update_newsletter_draft_status(draft["id"], "sent" if success else "failed")
        if success:
            logger.info("[V2] Recording posts into reddit_posts...")
            db.upsert_reddit_posts(selected_posts)
            db.log_newsletter_send(posts_count=len(selected_posts), success=True, recipients=recipients, editor_words=editor_words, newsletter_title=config.get_newsletter_title())
            logger.info("Newsletter sent successfully")
        else:
            logger.error("Failed to send newsletter")
            db.log_newsletter_send(posts_count=len(selected_posts), success=False, error_message="Failed to send newsletter", recipients=recipients)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== Job completed in {duration:.2f}s ===")
    except Exception as e:
        logger.error(f"Error in scraper job: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"=== Job failed after {duration:.2f}s ===")
        sys.exit(1)


if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    force_resend = "--force-resend" in sys.argv
    run_scraper_job(test_mode=test_mode, force_resend=force_resend)
