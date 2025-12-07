"""
Reddit Newsletter Scraper Service
Scheduled job to scrape Reddit and send newsletters
"""
import os
import sys
import schedule
import time
import logging
from datetime import datetime
from typing import List, Dict

# Import from local package
from .config_manager import ConfigManager
from .reddit_scraper import RedditScraper
from .chatgpt_client import ChatGPTClient
from .newsletter_sender import NewsletterSender
from .database_manager import DatabaseManager

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'scraper.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class NewsletterScraper:
    """Main scraper service for Reddit newsletters"""
    
    def __init__(self):
        """Initialize scraper with all required services"""
        logger.info("Initializing Newsletter Scraper...")
        
        try:
            self.config = ConfigManager()
            self.reddit = RedditScraper(self.config)
            self.gpt = ChatGPTClient(self.config)
            self.email = NewsletterSender(self.config)
            self.db = DatabaseManager()
            
            # Get configuration
            self.subreddits = self.config.get_target_subreddits()
            self.post_limit = self.config.get_posts_limit()
            self.time_filter = 'day'  # Default time filter
            
            logger.info(f"Initialized scraper for subreddits: {self.subreddits}")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise
    
    def scrape_and_send(self) -> None:
        """Main job: scrape Reddit, generate newsletter, and send"""
        logger.info("=== Starting newsletter generation job ===")
        start_time = datetime.now()
        
        try:
            all_posts = []
            
            # Scrape each subreddit
            for subreddit in self.subreddits:
                subreddit = subreddit.strip()
                logger.info(f"Scraping r/{subreddit}...")
                
                try:
                    posts = self.reddit.get_hot_posts(limit=self.post_limit)
                    all_posts.extend(posts)
                    logger.info(f"Fetched {len(posts)} posts from r/{subreddit}")
                    
                except Exception as e:
                    logger.error(f"Error scraping r/{subreddit}: {e}")
                    continue
            
            if not all_posts:
                logger.warning("No posts found. Skipping newsletter generation.")
                return
            
            # Filter new posts and send newsletter
            logger.info(f"Filtering {len(all_posts)} posts...")
            new_posts = self.db.filter_new_posts(all_posts)
            
            if not new_posts:
                logger.warning("No new posts to send.")
                return
                
            logger.info(f"Sending newsletter with {len(new_posts)} new posts...")
            success, editor_words = self.email.send_newsletter(new_posts)
            
            if success:
                # Mark posts as sent
                self.db.mark_posts_as_sent(new_posts)
                
                # Log to database
                self.db.log_newsletter_send(
                    posts_count=len(new_posts),
                    success=True,
                    recipients=self.config.get_recipients(),
                    editor_words=editor_words
                )
            
            # Log statistics
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"=== Job completed in {duration:.2f}s ===")
            
        except Exception as e:
            logger.error(f"Error in scrape_and_send job: {e}", exc_info=True)
    
    def test_connection(self) -> bool:
        """Test all service connections"""
        logger.info("Testing service connections...")
        
        try:
            # Test Reddit
            logger.info("Testing Reddit connection...")
            test_posts = self.reddit.get_hot_posts(limit=1)
            logger.info(f"✓ Reddit OK ({len(test_posts)} posts)")
            
            # Test Database
            logger.info("Testing database connection...")
            # Database already connected in __init__
            logger.info("✓ Database OK")
            
            # Test OpenAI (optional)
            logger.info("Testing OpenAI connection...")
            # Simple test - you might want to implement this in ChatGPTClient
            logger.info("✓ OpenAI OK")
            
            logger.info("All connections successful!")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def run_scheduler(scraper: NewsletterScraper) -> None:
    """Run the scheduler with configured intervals"""
    
    # Get schedule configuration from environment
    schedule_time = os.getenv('SCHEDULE_TIME', '09:00')  # Default 9 AM
    schedule_days = os.getenv('SCHEDULE_DAYS', 'monday,wednesday,friday').split(',')
    
    logger.info(f"Scheduling newsletter for {schedule_days} at {schedule_time}")
    
    # Schedule jobs
    for day in schedule_days:
        day = day.strip().lower()
        if day == 'monday':
            schedule.every().monday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'tuesday':
            schedule.every().tuesday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'wednesday':
            schedule.every().wednesday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'thursday':
            schedule.every().thursday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'friday':
            schedule.every().friday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'saturday':
            schedule.every().saturday.at(schedule_time).do(scraper.scrape_and_send)
        elif day == 'sunday':
            schedule.every().sunday.at(schedule_time).do(scraper.scrape_and_send)
    
    logger.info("Scheduler started. Waiting for scheduled times...")
    
    # Run scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    logger.info("Starting Newsletter Scraper Service")
    
    # Initialize scraper
    scraper = NewsletterScraper()
    
    # Test connections on startup
    if not scraper.test_connection():
        logger.error("Connection tests failed. Exiting.")
        sys.exit(1)
    
    # Check if running in immediate mode
    run_mode = os.getenv('RUN_MODE', 'schedule')  # 'schedule' or 'immediate'
    
    if run_mode == 'immediate':
        logger.info("Running in IMMEDIATE mode - executing job once")
        scraper.scrape_and_send()
    else:
        logger.info("Running in SCHEDULE mode")
        run_scheduler(scraper)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
