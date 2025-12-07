"""Database Manager - PostgreSQL 数据库管理模块"""

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """PostgreSQL 数据库管理器"""

    def __init__(self):
        self.config = ConfigManager()
        self.connection = None
        self._connect()
        self._initialize_database()

    def _connect(self):
        """连接到 PostgreSQL 数据库"""
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
        """初始化 PostgreSQL 数据库表结构"""
        try:
            cursor = self.connection.cursor()

            # 创建帖子表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id VARCHAR(50) PRIMARY KEY,
                    title TEXT NOT NULL,
                    author VARCHAR(100),
                    url TEXT,
                    permalink TEXT,
                    subreddit VARCHAR(100),
                    score INTEGER,
                    num_comments INTEGER,
                    created_utc TIMESTAMP,
                    selftext TEXT,
                    is_video BOOLEAN,
                    over_18 BOOLEAN,
                    sent_at TIMESTAMP,
                    data_json JSONB,
                    gpt_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 创建发送记录表
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

            # 创建配置表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 创建索引
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_posts_sent_at 
                ON posts(sent_at)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_posts_subreddit 
                ON posts(subreddit)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_newsletter_logs_sent_at 
                ON newsletter_logs(sent_at)
            """
            )

            # 添加评论字段（如果不存在）
            self._migrate_add_comment_fields(cursor)

            cursor.close()
            logger.info("PostgreSQL database tables initialized successfully")

        except psycopg2.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def _migrate_add_comment_fields(self, cursor):
        """添加评论相关字段"""
        try:
            # 检查字段是否已存在
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

    def filter_new_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        过滤出未发送过的新帖子

        Args:
            posts: 帖子列表

        Returns:
            新帖子列表
        """
        try:
            cursor = self.connection.cursor()

            new_posts = []
            for post in posts:
                cursor.execute("SELECT id FROM posts WHERE id = %s", (post["id"],))
                if not cursor.fetchone():
                    new_posts.append(post)

            cursor.close()
            logger.info(f"Filtered {len(new_posts)} new posts (total {len(posts)} posts)")
            return new_posts

        except psycopg2.Error as e:
            logger.error(f"Error filtering new posts: {e}")
            return posts  # 出错时返回所有帖子

    def mark_posts_as_sent(self, posts: List[Dict]) -> bool:
        """
        标记帖子为已发送

        Args:
            posts: 帖子列表

        Returns:
            操作是否成功
        """
        try:
            cursor = self.connection.cursor()

            sent_time = datetime.now()

            for post in posts:
                cursor.execute(
                    """
                    INSERT INTO posts 
                    (id, title, author, url, permalink, subreddit, score, 
                     num_comments, created_utc, selftext, is_video, over_18, 
                     sent_at, data_json, gpt_summary, top_comments, comment_summary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        sent_at = EXCLUDED.sent_at,
                        data_json = EXCLUDED.data_json,
                        gpt_summary = EXCLUDED.gpt_summary,
                        top_comments = EXCLUDED.top_comments,
                        comment_summary = EXCLUDED.comment_summary
                """,
                    (
                        post["id"],
                        post["title"],
                        post["author"],
                        post["url"],
                        post["permalink"],
                        post["subreddit"],
                        post["score"],
                        post["num_comments"],
                        (
                            datetime.fromtimestamp(post["created_utc"])
                            if isinstance(post["created_utc"], (int, float))
                            else post["created_utc"]
                        ),
                        post.get("selftext", ""),
                        post["is_video"],
                        post["over_18"],
                        sent_time,
                        json.dumps(post, ensure_ascii=False),
                        post.get("gpt_summary", ""),
                        json.dumps(post.get("top_comments", []), ensure_ascii=False),
                        post.get("comment_summary", ""),
                    ),
                )

            cursor.close()
            logger.info(f"Marked {len(posts)} posts as sent")
            return True

        except psycopg2.Error as e:
            logger.error(f"Error marking posts as sent: {e}")
            return False

    def log_newsletter_send(
        self,
        posts_count: int,
        success: bool,
        error_message: str = None,
        recipients: List[str] = None,
        editor_words: str = None,
        newsletter_title: str = None,
    ) -> bool:
        """
        记录Newsletter发送日志

        Args:
            posts_count: 帖子数量
            success: 是否成功
            error_message: 错误信息
            recipients: 收件人列表
            editor_words: 编辑寄语
            newsletter_title: Newsletter标题

        Returns:
            操作是否成功
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                INSERT INTO newsletter_logs 
                (posts_count, success, error_message, recipients, editor_words, newsletter_title)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    posts_count,
                    success,
                    error_message,
                    json.dumps(recipients) if recipients else None,
                    editor_words,
                    newsletter_title,
                ),
            )

            cursor.close()
            return True

        except psycopg2.Error as e:
            logger.error(f"Error logging newsletter send: {e}")
            return False

    def get_recent_posts(self, days: int = 7) -> List[Dict]:
        """
        获取最近几天发送的帖子

        Args:
            days: 天数

        Returns:
            帖子列表
        """
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cursor.execute(
                """
                SELECT * FROM posts 
                WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                ORDER BY sent_at DESC
            """,
                (days,),
            )

            rows = cursor.fetchall()

            posts = []
            for row in rows:
                post_dict = dict(row)
                if post_dict["data_json"]:
                    try:
                        additional_data = (
                            json.loads(post_dict["data_json"])
                            if isinstance(post_dict["data_json"], str)
                            else post_dict["data_json"]
                        )
                        post_dict.update(additional_data)
                    except (json.JSONDecodeError, TypeError):
                        pass
                posts.append(post_dict)

            cursor.close()
            return posts

        except psycopg2.Error as e:
            logger.error(f"Error getting recent posts: {e}")
            return []

    def get_newsletter_stats(self, days: int = 30) -> Dict:
        """
        获取Newsletter统计信息

        Args:
            days: 统计天数

        Returns:
            统计信息字典
        """
        try:
            cursor = self.connection.cursor()

            # 总发送次数
            cursor.execute(
                """
                SELECT COUNT(*) FROM newsletter_logs 
                WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            """,
                (days,),
            )
            total_sends = cursor.fetchone()[0]

            # 成功发送次数
            cursor.execute(
                """
                SELECT COUNT(*) FROM newsletter_logs 
                WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days' AND success = true
            """,
                (days,),
            )
            successful_sends = cursor.fetchone()[0]

            # 总帖子数
            cursor.execute(
                """
                SELECT COUNT(*) FROM posts 
                WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            """,
                (days,),
            )
            total_posts = cursor.fetchone()[0]

            # 最后发送时间
            cursor.execute(
                """
                SELECT MAX(sent_at) FROM newsletter_logs 
                WHERE success = true
            """
            )
            last_send_result = cursor.fetchone()
            last_send = last_send_result[0] if last_send_result and last_send_result[0] else None

            cursor.close()

            return {
                "total_sends": total_sends,
                "successful_sends": successful_sends,
                "success_rate": successful_sends / total_sends if total_sends > 0 else 0,
                "total_posts": total_posts,
                "last_send": last_send,
                "days": days,
            }

        except psycopg2.Error as e:
            logger.error(f"Error getting newsletter stats: {e}")
            return {}

    def cleanup_old_data(self, days: int = 90):
        """
        清理旧数据

        Args:
            days: 保留天数
        """
        try:
            cursor = self.connection.cursor()

            # 删除旧帖子记录
            cursor.execute(
                """
                DELETE FROM posts 
                WHERE sent_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """,
                (days,),
            )
            deleted_posts = cursor.rowcount

            # 删除旧日志记录
            cursor.execute(
                """
                DELETE FROM newsletter_logs 
                WHERE sent_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """,
                (days,),
            )
            deleted_logs = cursor.rowcount

            cursor.close()
            logger.info(f"Cleanup completed: deleted {deleted_posts} post records and {deleted_logs} log records")

        except psycopg2.Error as e:
            logger.error(f"Error cleaning old data: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL database connection closed")

    def get_newsletter_history(self, limit: int = 10) -> List[Dict]:
        """
        获取Newsletter发送历史

        Args:
            limit: 返回记录数量限制

        Returns:
            历史记录列表
        """
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
                history.append(
                    {
                        "id": row["id"],
                        "sent_at": row["sent_at"],
                        "posts_count": row["posts_count"],
                        "success": row["success"],
                        "error_message": row["error_message"],
                        "recipients": json.loads(row["recipients"]) if row["recipients"] else [],
                        "editor_words": row["editor_words"],
                        "newsletter_title": row["newsletter_title"],
                    }
                )

            cursor.close()
            return history

        except psycopg2.Error as e:
            logger.error(f"Error getting newsletter history: {e}")
            return []

    def get_posts_with_summaries(self, limit: int = 20) -> List[Dict]:
        """
        获取带有GPT总结的帖子

        Args:
            limit: 返回记录数量限制

        Returns:
            帖子列表
        """
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cursor.execute(
                """
                SELECT id, title, author, subreddit, score, num_comments,
                       sent_at, gpt_summary, data_json
                FROM posts 
                WHERE gpt_summary IS NOT NULL AND gpt_summary != ''
                ORDER BY sent_at DESC 
                LIMIT %s
            """,
                (limit,),
            )

            rows = cursor.fetchall()

            posts = []
            for row in rows:
                posts.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "author": row["author"],
                        "subreddit": row["subreddit"],
                        "score": row["score"],
                        "num_comments": row["num_comments"],
                        "sent_at": row["sent_at"],
                        "gpt_summary": row["gpt_summary"],
                        "data_json": row["data_json"],
                    }
                )

            cursor.close()
            return posts

        except psycopg2.Error as e:
            logger.error(f"Error getting posts with summaries: {e}")
            return []

    def get_total_posts_count(self) -> int:
        """获取数据库中总帖子数量"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except psycopg2.Error as e:
            logger.error(f"Error getting total posts count: {e}")
            return 0

    def clear_all_history(self):
        """清空所有历史记录"""
        try:
            cursor = self.connection.cursor()

            # 清空表数据
            tables_to_clear = ["posts", "newsletter_logs", "settings"]

            for table in tables_to_clear:
                # 检查表是否存在
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
        """获取数据库连接信息"""
        try:
            db_config = self.config.get_database_config()
            return {
                "type": "postgresql",
                "host": db_config.get("host"),
                "port": db_config.get("port"),
                "database": db_config.get("database"),
                "user": db_config.get("user"),
                "connected": self.connection and not self.connection.closed,
            }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"type": "postgresql", "connected": False}
