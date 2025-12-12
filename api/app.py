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
