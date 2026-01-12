"""
Reddit Newsletter API - V2 FastAPI App
Migrated into app/backend/api for unified backend.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import logging
import os
import asyncio

# Import existing backend services
from backend.scraper.config_manager import ConfigManager
from backend.scraper.reddit_scraper import RedditScraper
from backend.scraper.chatgpt_client import ChatGPTClient
from backend.scraper.newsletter_sender import NewsletterSender
from backend.scraper.database_manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reddit Newsletter API",
    description="API for managing Reddit newsletter subscriptions and delivery (V2)",
    version="2.0.0"
)

# Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class NewsletterRequest(BaseModel):
    subreddit: str
    limit: Optional[int] = 10
    time_filter: Optional[str] = "day"

class SubscribeRequest(BaseModel):
    email: EmailStr
    subreddits: List[str]

# Global services
config_manager: ConfigManager | None = None
reddit_scraper: RedditScraper | None = None
chatgpt_client: ChatGPTClient | None = None
newsletter_sender: NewsletterSender | None = None
db_manager: DatabaseManager | None = None

INIT_IN_BACKGROUND = os.getenv("INIT_IN_BACKGROUND", "false").lower() == "true"

async def _initialize_services():
    global config_manager, reddit_scraper, chatgpt_client, newsletter_sender, db_manager
    logger.info("Initializing V2 services...")
    config_manager = ConfigManager()
    reddit_scraper = RedditScraper(config_manager)
    chatgpt_client = ChatGPTClient(config_manager)
    newsletter_sender = NewsletterSender(config_manager)
    db_manager = DatabaseManager()
    logger.info("Services initialized")

@app.on_event("startup")
async def startup_event():
    try:
        if INIT_IN_BACKGROUND:
            # Do not block startup; initialize services in background
            asyncio.create_task(_initialize_services())
        else:
            await _initialize_services()
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Do not re-raise to allow health endpoint to report status

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down services...")
    if db_manager:
        db_manager.close()

@app.get("/", response_model=HealthResponse)
async def root():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        initializing = not all([config_manager, reddit_scraper, chatgpt_client, newsletter_sender, db_manager])
        if initializing:
            return {"status": "initializing", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}
        # Optionally validate DB connectivity when ready
        db_manager.test_connection()
        return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/posts/{subreddit}")
async def get_posts(subreddit: str, limit: int = 10, time_filter: str = "day"):
    try:
        if not reddit_scraper:
            raise HTTPException(status_code=503, detail="Reddit service not initialized")
        posts = reddit_scraper.fetch_top_posts(subreddit=subreddit, limit=limit, time_filter=time_filter)
        return {"subreddit": subreddit, "count": len(posts), "posts": posts, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/newsletter/send")
async def send_newsletter(background_tasks: BackgroundTasks, request: NewsletterRequest):
    try:
        if not all([reddit_scraper, chatgpt_client, newsletter_sender]):
            raise HTTPException(status_code=503, detail="Services not initialized")
        background_tasks.add_task(process_newsletter, request.subreddit, request.limit, request.time_filter)
        return {"status": "processing", "message": f"Newsletter generation started for r/{request.subreddit}", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error sending newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        # Minimal stats placeholder; can be expanded to use V2 tables
        return {"timestamp": datetime.now().isoformat(), "status": "operational"}
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        # TODO: implement V2 subscription using users table
        return {"status": "success", "message": f"Subscribed {request.email} to {len(request.subreddits)} subreddits", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_newsletter(subreddit: str, limit: int, time_filter: str):
    try:
        logger.info(f"Processing newsletter for r/{subreddit}")
        posts = reddit_scraper.fetch_top_posts(subreddit, limit, time_filter)
        summary = chatgpt_client.generate_summary(posts)
        newsletter_sender.send(summary)
        logger.info(f"Newsletter sent successfully for r/{subreddit}")
    except Exception as e:
        logger.error(f"Error processing newsletter: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
