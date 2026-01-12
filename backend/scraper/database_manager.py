"""Database Manager - moved to app/backend/scraper"""

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime, date
from typing import List, Dict
import json
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.config = ConfigManager()
        self.connection = None
        self._connect()
        self._initialize_database()

    def _connect(self):
        try:
            db_config = self.config.get_database_config()
            self.connection = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                sslmode=db_config.get("sslmode", "prefer"),
            )
            self.connection.autocommit = True
            logger.info("Successfully connected to PostgreSQL database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _initialize_database(self):
        try:
            cursor = self.connection.cursor()
            # V2 core tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS subreddits (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    daily_hot_post_ids JSONB DEFAULT '[]'::jsonb,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_fetched_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reddit_posts (
                    id VARCHAR(50) PRIMARY KEY,
                    subreddit_id INTEGER REFERENCES subreddits(id),
                    title TEXT,
                    url TEXT,
                    num_comments INTEGER,
                    score INTEGER,
                    created_utc TIMESTAMP,
                    selftext TEXT,
                    over_18 BOOLEAN,
                    gpt_summary TEXT,
                    gpt_summary_en TEXT,
                    gpt_processed_at TIMESTAMP,
                    gpt_error TEXT,
                    fetch_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS newsletter_logs (
                    id SERIAL PRIMARY KEY,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    posts_count INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    recipients JSONB,
                    editor_words TEXT,
                    newsletter_title TEXT
                )
            """
            )
            # Indexes per V2 schema
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_subreddits_is_active
                ON subreddits(is_active)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_subreddits_last_fetched
                ON subreddits(last_fetched_at)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_subreddit_id
                ON reddit_posts(subreddit_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_fetch_date
                ON reddit_posts(fetch_date)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_score
                ON reddit_posts(score)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_newsletter_logs_sent_at 
                ON newsletter_logs(sent_at)
            """
            )
            cursor.close()
            logger.info("PostgreSQL database tables initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def _migrate_add_comment_fields(self, cursor):
        try:
            cursor.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'posts' AND column_name = 'top_comments'
                """
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    ALTER TABLE posts 
                    ADD COLUMN top_comments JSONB,
                    ADD COLUMN comment_summary TEXT
                    """
                )
                logger.info("Successfully added comment fields")
        except psycopg2.Error as e:
            logger.warning(f"Error adding comment fields (may already exist): {e}")

    def test_connection(self) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    # Legacy V1 helpers removed: filter_new_posts, mark_posts_as_sent

    def log_newsletter_send(self, posts_count: int, success: bool, error_message: str = None, recipients: List[str] = None, editor_words: str = None, newsletter_title: str = None) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO newsletter_logs 
                (posts_count, success, error_message, recipients, editor_words, newsletter_title)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (posts_count, success, error_message, json.dumps(recipients) if recipients else None, editor_words, newsletter_title,),
            )
            cursor.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"Error logging newsletter send: {e}")
            return False

    # ===== V2 helpers for subreddits + reddit_posts =====
    def ensure_subreddit(self, name: str) -> int:
        """Get or create a subreddit row and return its id."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM subreddits WHERE name = %s", (name,))
            row = cursor.fetchone()
            if row:
                cursor.close()
                return row[0]
            cursor.execute(
                """
                INSERT INTO subreddits (name, description, daily_hot_post_ids, is_active, last_fetched_at, created_at)
                VALUES (%s, NULL, '[]'::jsonb, TRUE, NULL, CURRENT_TIMESTAMP)
                RETURNING id
                """,
                (name,),
            )
            new_id = cursor.fetchone()[0]
            cursor.close()
            return new_id
        except psycopg2.Error as e:
            logger.error(f"ensure_subreddit failed: {e}")
            raise

    def reddit_post_exists(self, post_id: str) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM reddit_posts WHERE id = %s", (post_id,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except psycopg2.Error as e:
            logger.error(f"reddit_post_exists failed: {e}")
            return False

    def filter_new_posts_v2(self, posts: List[Dict]) -> List[Dict]:
        """Return posts whose id is not present in reddit_posts."""
        try:
            cursor = self.connection.cursor()
            ids = [p["id"] for p in posts]
            # Fetch existing ids in a single query
            cursor.execute(
                "SELECT id FROM reddit_posts WHERE id = ANY(%s)", (ids,)
            )
            existing = {row[0] for row in cursor.fetchall()}
            cursor.close()
            new_posts = [p for p in posts if p["id"] not in existing]
            logger.info(f"[V2] Filtered {len(new_posts)} new posts (total {len(posts)} posts)")
            return new_posts
        except psycopg2.Error as e:
            logger.error(f"filter_new_posts_v2 failed: {e}")
            return posts

    def upsert_reddit_post(self, post: Dict) -> bool:
        """Insert or update a single post into reddit_posts table."""
        try:
            subreddit_id = self.ensure_subreddit(post["subreddit"]) if post.get("subreddit") else None
            cursor = self.connection.cursor()
            created_ts = (
                datetime.fromtimestamp(post["created_utc"]) if isinstance(post["created_utc"], (int, float)) else post["created_utc"]
            )
            gpt_summary = post.get("gpt_summary") or None
            gpt_processed_at = (datetime.now() if gpt_summary else None)
            cursor.execute(
                """
                INSERT INTO reddit_posts (
                    id, subreddit_id, title, url, num_comments, score,
                    created_utc, selftext, over_18, gpt_summary,
                    gpt_processed_at, gpt_error, fetch_date, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, CURRENT_TIMESTAMP
                )
                ON CONFLICT (id) DO UPDATE SET
                    subreddit_id = EXCLUDED.subreddit_id,
                    title = EXCLUDED.title,
                    url = EXCLUDED.url,
                    num_comments = EXCLUDED.num_comments,
                    score = EXCLUDED.score,
                    created_utc = EXCLUDED.created_utc,
                    selftext = EXCLUDED.selftext,
                    over_18 = EXCLUDED.over_18,
                    gpt_summary = COALESCE(EXCLUDED.gpt_summary, reddit_posts.gpt_summary),
                    gpt_processed_at = COALESCE(EXCLUDED.gpt_processed_at, reddit_posts.gpt_processed_at),
                    gpt_error = COALESCE(EXCLUDED.gpt_error, reddit_posts.gpt_error),
                    fetch_date = EXCLUDED.fetch_date
                """,
                (
                    post["id"],
                    subreddit_id,
                    post.get("title"),
                    post.get("url"),
                    post.get("num_comments"),
                    post.get("score"),
                    created_ts,
                    post.get("selftext", ""),
                    post.get("over_18", False),
                    gpt_summary,
                    gpt_processed_at,
                    None,
                    date.today(),
                ),
            )
            cursor.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"upsert_reddit_post failed: {e}")
            return False

    def upsert_reddit_posts(self, posts: List[Dict]) -> int:
        """Bulk upsert posts into reddit_posts; returns count of successful upserts."""
        count = 0
        for p in posts:
            if self.upsert_reddit_post(p):
                count += 1
        logger.info(f"[V2] Upserted {count} posts into reddit_posts")
        return count

    def get_recent_posts(self, days: int = 7) -> List[Dict]:
        """Return recent posts from reddit_posts filtered by fetch_date."""
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM reddit_posts 
                WHERE fetch_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY created_utc DESC NULLS LAST
                """,
                (days,),
            )
            rows = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            logger.error(f"Error getting recent posts: {e}")
            return []

    def get_newsletter_stats(self, days: int = 30) -> Dict:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT COUNT(*) FROM newsletter_logs WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'""", (days,))
            total_sends = cursor.fetchone()[0]
            cursor.execute("""SELECT COUNT(*) FROM newsletter_logs WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days' AND success = true""", (days,))
            successful_sends = cursor.fetchone()[0]
            cursor.execute("""SELECT COUNT(*) FROM reddit_posts WHERE fetch_date >= CURRENT_DATE - INTERVAL '%s days'""", (days,))
            total_posts = cursor.fetchone()[0]
            cursor.execute("""SELECT MAX(sent_at) FROM newsletter_logs WHERE success = true""")
            last_send_result = cursor.fetchone()
            last_send = last_send_result[0] if last_send_result and last_send_result[0] else None
            cursor.close()
            return {"total_sends": total_sends, "successful_sends": successful_sends, "success_rate": successful_sends / total_sends if total_sends > 0 else 0, "total_posts": total_posts, "last_send": last_send, "days": days}
        except psycopg2.Error as e:
            logger.error(f"Error getting newsletter stats: {e}")
            return {}

    def cleanup_old_data(self, days: int = 90):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""DELETE FROM reddit_posts WHERE fetch_date < CURRENT_DATE - INTERVAL '%s days'""", (days,))
            deleted_posts = cursor.rowcount
            cursor.execute("""DELETE FROM newsletter_logs WHERE sent_at < CURRENT_TIMESTAMP - INTERVAL '%s days'""", (days,))
            deleted_logs = cursor.rowcount
            cursor.close()
            logger.info(f"Cleanup completed: deleted {deleted_posts} reddit_post records and {deleted_logs} log records")
        except psycopg2.Error as e:
            logger.error(f"Error cleaning old data: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL database connection closed")

    def get_newsletter_history(self, limit: int = 10) -> List[Dict]:
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                """
                SELECT id, sent_at, posts_count, success, error_message, 
                       recipients, editor_words, newsletter_title
                FROM newsletter_logs 
                ORDER BY sent_at DESC 
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({"id": row["id"], "sent_at": row["sent_at"], "posts_count": row["posts_count"], "success": row["success"], "error_message": row["error_message"], "recipients": json.loads(row["recipients"]) if row["recipients"] else [], "editor_words": row["editor_words"], "newsletter_title": row["newsletter_title"]})
            cursor.close()
            return history
        except psycopg2.Error as e:
            logger.error(f"Error getting newsletter history: {e}")
            return []

    def get_posts_with_summaries(self, limit: int = 20) -> List[Dict]:
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, subreddit_id, score, num_comments,
                       created_utc, gpt_summary
                FROM reddit_posts 
                WHERE gpt_summary IS NOT NULL AND gpt_summary != ''
                ORDER BY created_utc DESC NULLS LAST
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "subreddit_id": row["subreddit_id"],
                    "score": row["score"],
                    "num_comments": row["num_comments"],
                    "created_utc": row["created_utc"],
                    "gpt_summary": row["gpt_summary"],
                }
                for row in rows
            ]
        except psycopg2.Error as e:
            logger.error(f"Error getting posts with summaries: {e}")
            return []

    def get_total_posts_count(self) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM reddit_posts")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except psycopg2.Error as e:
            logger.error(f"Error getting total posts count: {e}")
            return 0

    def clear_all_history(self):
        try:
            cursor = self.connection.cursor()
            tables_to_clear = ["reddit_posts", "newsletter_logs"]
            for table in tables_to_clear:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                    """,
                    (table,),
                )
                if cursor.fetchone()[0]:
                    cursor.execute(f"DELETE FROM {table}")
                    logger.info(f"Cleared table: {table}")
            cursor.close()
            logger.info("PostgreSQL database history cleared")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error clearing database history: {e}")
            return False

    def get_connection_info(self) -> Dict:
        try:
            db_config = self.config.get_database_config()
            return {"type": "postgresql", "host": db_config.get("host"), "port": db_config.get("port"), "database": db_config.get("database"), "user": db_config.get("user"), "connected": self.connection and not self.connection.closed}
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"type": "postgresql", "connected": False}
