#!/usr/bin/env python3
"""
Standalone scraper job entry point
Usage: python scraper/run_job.py [--test]
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.config_manager import ConfigManager
from scraper.reddit_scraper import RedditScraper
from scraper.chatgpt_client import ChatGPTClient
from scraper.newsletter_sender import NewsletterSender
from scraper.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_scraper_job(test_mode=False):
    """Run a single scraper job"""
    start_time = datetime.now()
    logger.info("=== Starting scraper job ===")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        config = ConfigManager()
        reddit = RedditScraper(config)
        chatgpt = ChatGPTClient(config)
        sender = NewsletterSender(config)
        db = DatabaseManager()
        
        logger.info("All services initialized successfully")
        
        # Test connections if in test mode
        if test_mode:
            logger.info("Testing connections...")
            
            # Test Reddit
            test_posts = reddit.get_hot_posts(limit=1)
            logger.info(f"✓ Reddit OK ({len(test_posts)} posts)")
            
            # Test Database
            if db.test_connection():
                logger.info("✓ Database OK")
            
            logger.info("All connections successful!")
            return
        
        # Get hot posts from Reddit
        logger.info("Fetching hot posts from Reddit...")
        posts_limit = config.get_posts_limit()
        posts = reddit.get_hot_posts(limit=posts_limit)
        logger.info(f"Fetched {len(posts)} posts from Reddit")
        
        # Filter new posts
        logger.info("Filtering new posts...")
        new_posts = db.filter_new_posts(posts)
        logger.info(f"Found {len(new_posts)} new posts")
        
        if not new_posts:
            logger.info("No new posts to send")
            return
        
        # Limit posts for newsletter
        newsletter_limit = config.get_newsletter_posts_limit()
        selected_posts = new_posts[:newsletter_limit]
        logger.info(f"Selected {len(selected_posts)} posts for newsletter")
        
        # Generate summaries using ChatGPT
        if config.get_enable_gpt_summaries():
            logger.info("Generating GPT summaries...")
            for post in selected_posts:
                try:
                    summary = chatgpt.summarize_and_analyze(post)
                    post['gpt_summary'] = summary
                    logger.info(f"Generated summary for: {post['title'][:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to generate summary for {post['id']}: {e}")
                    post['gpt_summary'] = None
        
        # Generate editor words
        if config.get_enable_editor_summary():
            logger.info("Generating editor words...")
            try:
                editor_words = chatgpt.generate_editor_words(selected_posts)
            except Exception as e:
                logger.warning(f"Failed to generate editor words: {e}")
                editor_words = None
        else:
            editor_words = None
        
        # Send newsletter
        logger.info("Sending newsletter...")
        success = sender.send_newsletter(selected_posts, editor_words)
        
        if success:
            # Mark posts as sent
            logger.info("Marking posts as sent in database...")
            db.mark_posts_as_sent(selected_posts)
            
            # Log newsletter send
            recipients = config.get_email_recipients()
            db.log_newsletter_send(
                posts_count=len(selected_posts),
                success=True,
                recipients=recipients,
                editor_words=editor_words,
                newsletter_title=config.get_newsletter_title()
            )
            
            logger.info("Newsletter sent successfully")
        else:
            logger.error("Failed to send newsletter")
            db.log_newsletter_send(
                posts_count=len(selected_posts),
                success=False,
                error_message="Failed to send newsletter",
                recipients=config.get_email_recipients()
            )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== Job completed in {duration:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Error in scraper job: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"=== Job failed after {duration:.2f}s ===")
        sys.exit(1)


if __name__ == "__main__":
    # Check for test flag
    test_mode = "--test" in sys.argv
    
    run_scraper_job(test_mode=test_mode)
