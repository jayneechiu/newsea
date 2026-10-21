"""
Reddit Newsletter API - V2 FastAPI App
Migrated into app/backend/api for unified backend.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import logging
import os
import asyncio
import hmac

# Import existing backend services
from backend.scraper.config_manager import ConfigManager
from backend.scraper.reddit_scraper import RedditScraper
from backend.scraper.chatgpt_client import ChatGPTClient
from backend.scraper.newsletter_sender import NewsletterSender
from backend.scraper.newsletter_composer import NewsletterComposer
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

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
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
    subreddits: List[str] = Field(default_factory=list)
    name: Optional[str] = None

class ReviewRequest(BaseModel):
    note: Optional[str] = None

# Global services
config_manager: Optional[ConfigManager] = None
reddit_scraper: Optional[RedditScraper] = None
chatgpt_client: Optional[ChatGPTClient] = None
newsletter_sender: Optional[NewsletterSender] = None
newsletter_composer: Optional[NewsletterComposer] = None
db_manager: Optional[DatabaseManager] = None

INIT_IN_BACKGROUND = os.getenv("INIT_IN_BACKGROUND", "false").lower() == "true"

def require_admin(x_newsea_admin_key: Optional[str] = Header(default=None)) -> None:
    expected_key = os.getenv("NEWSLETTER_ADMIN_KEY", "")
    if not expected_key:
        raise HTTPException(status_code=503, detail="Newsletter admin access is not configured")
    if not x_newsea_admin_key or not hmac.compare_digest(x_newsea_admin_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")

async def _initialize_services():
    global config_manager, reddit_scraper, chatgpt_client, newsletter_sender, newsletter_composer, db_manager
    logger.info("Initializing V2 services...")
    
    try:
        config_manager = ConfigManager()
        
        # 优先初始化数据库（不依赖Reddit）
        try:
            db_manager = DatabaseManager()
            logger.info("Database manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        
        # Reddit服务初始化失败不影响其他服务
        try:
            reddit_scraper = RedditScraper(config_manager)
            logger.info("Reddit scraper initialized successfully")
        except Exception as e:
            logger.warning(f"Reddit scraper initialization failed: {e}")
        
        try:
            chatgpt_client = ChatGPTClient(config_manager)
            logger.info("ChatGPT client initialized successfully")
        except Exception as e:
            logger.warning(f"ChatGPT client initialization failed: {e}")
        
        try:
            newsletter_sender = NewsletterSender(config_manager)
            logger.info("Newsletter sender initialized successfully")
        except Exception as e:
            logger.warning(f"Newsletter sender initialization failed: {e}")

        if reddit_scraper and chatgpt_client:
            newsletter_composer = NewsletterComposer(
                config_manager, reddit_scraper, chatgpt_client
            )
            
        logger.info("Services initialization completed")
    except Exception as e:
        logger.error(f"Critical error during services initialization: {e}")
        raise

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
        initializing = not all([config_manager, reddit_scraper, chatgpt_client, newsletter_sender, newsletter_composer, db_manager])
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

@app.get("/api/posts/db/recent")
async def get_recent_posts_from_db(days: int = 7, limit: int = 50):
    """Get recent posts from database"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        posts = db_manager.get_recent_posts(days=days)
        # Limit results
        posts = posts[:limit] if len(posts) > limit else posts
        return {"count": len(posts), "posts": posts, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching posts from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/db/with-summaries")
async def get_posts_with_summaries(limit: int = 20):
    """Get posts with GPT summaries from database"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        posts = db_manager.get_posts_with_summaries(limit=limit)
        return {"count": len(posts), "posts": posts, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching posts with summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/newsletter/send")
async def send_newsletter(
    background_tasks: BackgroundTasks,
    request: NewsletterRequest,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    try:
        require_admin(x_newsea_admin_key)
        if not all([newsletter_composer, newsletter_sender, db_manager]):
            raise HTTPException(status_code=503, detail="Services not initialized")
        recipients = db_manager.get_approved_newsletter_recipients()
        if not recipients:
            raise HTTPException(status_code=409, detail="No approved newsletter recipients")
        background_tasks.add_task(
            process_newsletter, request.subreddit, request.limit, request.time_filter, recipients
        )
        return {
            "status": "processing",
            "message": f"Newsletter generation started for r/{request.subreddit}",
            "recipient_count": len(recipients),
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/newsletter/latest")
async def get_latest_newsletter():
    """Expose the latest sent content package to the new app without recipient data."""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    draft = db_manager.get_latest_newsletter_draft(sent_only=True)
    if not draft:
        raise HTTPException(status_code=404, detail="No published newsletter yet")
    return {
        "id": draft["id"],
        "subreddit": draft["subreddit"],
        "posts": draft["posts"],
        "editor_words": draft["editor_words"],
        "published_at": draft["sent_at"],
    }

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

@app.post("/api/newsletter/subscriptions", status_code=202)
@app.post("/api/subscribe", status_code=202)
async def subscribe(request: SubscribeRequest):
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not initialized")
        subscription = db_manager.request_newsletter_subscription(
            str(request.email), request.subreddits, request.name
        )
        return {
            "status": "pending",
            "message": "Application received. The Newsea owner must approve it before any email is sent.",
            "subscription_id": subscription["id"],
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/newsletter/subscriptions")
async def list_subscriptions(
    status: Optional[str] = "pending",
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_newsea_admin_key)
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    if status and status not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=422, detail="Invalid subscription status")
    subscriptions = db_manager.list_newsletter_subscriptions(status)
    return {"count": len(subscriptions), "subscriptions": subscriptions}

@app.post("/api/admin/newsletter/drafts")
async def create_newsletter_draft(
    request: NewsletterRequest,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    """Fetch and enrich once, then persist the exact preview/send payload."""
    require_admin(x_newsea_admin_key)
    if not all([newsletter_composer, db_manager]):
        raise HTTPException(status_code=503, detail="Newsletter services not initialized")
    try:
        package = newsletter_composer.compose(
            request.subreddit, request.limit, request.time_filter, use_ai=True
        )
        draft = db_manager.create_newsletter_draft(package)
        return {"status": "draft", "draft": draft}
    except Exception as e:
        logger.error(f"Error creating newsletter draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/newsletter/drafts/{draft_id}")
async def get_newsletter_draft(
    draft_id: str,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_newsea_admin_key)
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    draft = db_manager.get_newsletter_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Newsletter draft not found")
    return {"draft": draft}

@app.post("/api/admin/newsletter/drafts/{draft_id}/send")
async def send_newsletter_draft(
    draft_id: str,
    background_tasks: BackgroundTasks,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_newsea_admin_key)
    if not all([newsletter_sender, db_manager]):
        raise HTTPException(status_code=503, detail="Newsletter services not initialized")
    draft = db_manager.get_newsletter_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Newsletter draft not found")
    recipients = db_manager.get_approved_newsletter_recipients()
    if not recipients:
        raise HTTPException(status_code=409, detail="No approved newsletter recipients")
    db_manager.update_newsletter_draft_status(draft_id, "sending")
    background_tasks.add_task(process_newsletter_draft, draft, recipients)
    return {"status": "sending", "draft_id": draft_id, "recipient_count": len(recipients)}

@app.post("/api/admin/newsletter/subscriptions/{subscription_id}/approve")
async def approve_subscription(
    subscription_id: int,
    request: ReviewRequest,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_newsea_admin_key)
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    subscription = db_manager.review_newsletter_subscription(
        subscription_id, "approved", note=request.note
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "approved", "subscription": subscription}

@app.post("/api/admin/newsletter/subscriptions/{subscription_id}/reject")
async def reject_subscription(
    subscription_id: int,
    request: ReviewRequest,
    x_newsea_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_newsea_admin_key)
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    subscription = db_manager.review_newsletter_subscription(
        subscription_id, "rejected", note=request.note
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "rejected", "subscription": subscription}

async def process_newsletter(
    subreddit: str, limit: int, time_filter: str, recipients: List[str]
):
    try:
        logger.info(f"Processing newsletter for r/{subreddit}")
        package = newsletter_composer.compose(subreddit, limit, time_filter, use_ai=True)
        draft = db_manager.create_newsletter_draft(package)
        await process_newsletter_draft(draft, recipients)
    except Exception as e:
        logger.error(f"Error processing newsletter: {e}")

async def process_newsletter_draft(draft: dict, recipients: List[str]):
    """Send exactly the persisted draft; never fetch or regenerate content here."""
    try:
        draft_id = draft["id"]
        db_manager.update_newsletter_draft_status(draft_id, "sending")
        posts = draft["posts"]
        editor_words = draft.get("editor_words")
        success, editor_words = newsletter_sender.send_newsletter(
            posts, editor_words, recipients=recipients
        )
        if db_manager:
            db_manager.log_newsletter_send(
                len(posts), success, None if success else "SMTP send failed", recipients, editor_words
            )
            db_manager.update_newsletter_draft_status(draft_id, "sent" if success else "failed")
        if success:
            logger.info(f"Newsletter draft {draft_id} sent successfully")
        else:
            logger.error(f"Newsletter draft {draft_id} send failed")
    except Exception as e:
        logger.error(f"Error sending newsletter draft: {e}")
        if db_manager and draft.get("id"):
            db_manager.update_newsletter_draft_status(draft["id"], "failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
