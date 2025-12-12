"""
Reddit Newsletter API - Azure Deployment
Fast API application for Reddit newsletter system
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from datetime import datetime
import logging
import sys
from pathlib import Path

# Import from scraper package
from scraper.config_manager import ConfigManager
from scraper.reddit_scraper import RedditScraper
from scraper.chatgpt_client import ChatGPTClient
from scraper.newsletter_sender import NewsletterSender
from scraper.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Reddit Newsletter API",
    description="API for managing Reddit newsletter subscriptions and delivery",
    version="1.0.0"
)

# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class NewsletterRequest(BaseModel):
    subreddit: str
    limit: Optional[int] = 10
    time_filter: Optional[str] = "day"

class EmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    content: str

class SubscribeRequest(BaseModel):
    email: EmailStr
    subreddits: List[str]

# Global instances (initialized on startup)
config_manager = None
reddit_scraper = None
chatgpt_client = None
newsletter_sender = None
db_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global config_manager, reddit_scraper, chatgpt_client, newsletter_sender, db_manager
    
    try:
        logger.info("Initializing services...")
        
        # Load configuration
        config_manager = ConfigManager()
        
        # Initialize components
        reddit_scraper = RedditScraper(config_manager)
        chatgpt_client = ChatGPTClient(config_manager)
        newsletter_sender = NewsletterSender(config_manager)
        db_manager = DatabaseManager()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services...")
    if db_manager:
        db_manager.close()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        if db_manager:
            db_manager.test_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/posts/{subreddit}")
async def get_posts(
    subreddit: str,
    limit: int = 10,
    time_filter: str = "day"
):
    """Fetch posts from a subreddit"""
    try:
        if not reddit_scraper:
            raise HTTPException(status_code=503, detail="Reddit service not initialized")
        
        posts = reddit_scraper.fetch_top_posts(
            subreddit=subreddit,
            limit=limit,
            time_filter=time_filter
        )
        
        return {
            "subreddit": subreddit,
            "count": len(posts),
            "posts": posts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/newsletter/send")
async def send_newsletter(
    background_tasks: BackgroundTasks,
    request: NewsletterRequest
):
    """Generate and send newsletter"""
    try:
        if not all([reddit_scraper, chatgpt_client, newsletter_sender]):
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Add task to background
        background_tasks.add_task(
            process_newsletter,
            request.subreddit,
            request.limit,
            request.time_filter
        )
        
        return {
            "status": "processing",
            "message": f"Newsletter generation started for r/{request.subreddit}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error sending newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scraper/run")
async def trigger_scraper_job(background_tasks: BackgroundTasks):
    """Manually trigger a scraper job"""
    try:
        if not all([reddit_scraper, chatgpt_client, newsletter_sender, db_manager]):
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Add scraper job to background
        background_tasks.add_task(run_scraper_job)
        
        return {
            "status": "started",
            "message": "Scraper job started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting scraper job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_newsletter(subreddit: str, limit: int, time_filter: str):
    """Background task to process newsletter"""
    try:
        logger.info(f"Processing newsletter for r/{subreddit}")
        
        # Fetch posts
        posts = reddit_scraper.fetch_top_posts(subreddit, limit, time_filter)
        
        # Generate summary
        summary = chatgpt_client.generate_summary(posts)
        
        # Send newsletter
        newsletter_sender.send(summary)
        
        logger.info(f"Newsletter sent successfully for r/{subreddit}")
    except Exception as e:
        logger.error(f"Error processing newsletter: {e}")

def run_scraper_job():
    """Background task to run complete scraper job"""
    try:
        logger.info("=== Starting scraper job ===")
        
        # Get hot posts from Reddit
        posts_limit = config_manager.get_posts_limit()
        posts = reddit_scraper.get_hot_posts(limit=posts_limit)
        logger.info(f"Fetched {len(posts)} posts from Reddit")
        
        # Filter new posts
        new_posts = db_manager.filter_new_posts(posts)
        logger.info(f"Found {len(new_posts)} new posts")
        
        if not new_posts:
            logger.info("No new posts to send")
            return
        
        # Limit posts for newsletter
        newsletter_limit = config_manager.get_newsletter_posts_limit()
        selected_posts = new_posts[:newsletter_limit]
        logger.info(f"Selected {len(selected_posts)} posts for newsletter")
        
        # Generate summaries using ChatGPT
        if config_manager.get_enable_gpt_summaries():
            for post in selected_posts:
                try:
                    summary = chatgpt_client.summarize_and_analyze(post)
                    post['gpt_summary'] = summary
                except Exception as e:
                    logger.warning(f"Failed to generate summary for {post['id']}: {e}")
                    post['gpt_summary'] = None
        
        # Generate editor words
        if config_manager.get_enable_editor_summary():
            try:
                editor_words = chatgpt_client.generate_editor_words(selected_posts)
            except Exception as e:
                logger.warning(f"Failed to generate editor words: {e}")
                editor_words = None
        else:
            editor_words = None
        
        # Send newsletter
        success = newsletter_sender.send_newsletter(selected_posts, editor_words)
        
        if success:
            db_manager.mark_posts_as_sent(selected_posts)
            recipients = config_manager.get_email_recipients()
            db_manager.log_newsletter_send(
                posts_count=len(selected_posts),
                success=True,
                recipients=recipients,
                editor_words=editor_words,
                newsletter_title=config_manager.get_newsletter_title()
            )
            logger.info("Newsletter sent successfully")
        else:
            logger.error("Failed to send newsletter")
            
        logger.info("=== Scraper job completed ===")
        
    except Exception as e:
        logger.error(f"Error in scraper job: {e}", exc_info=True)

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Get stats from database
        stats = {
            "timestamp": datetime.now().isoformat(),
            "status": "operational"
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    """Subscribe to newsletter"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Add subscription logic here
        return {
            "status": "success",
            "message": f"Subscribed {request.email} to {len(request.subreddits)} subreddits",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable in production
        log_level="info"
    )
