"""
数据库 Schema V2 - moved to app/backend/scraper
"""

import psycopg2
import psycopg2.extras
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseSchemaV2:
    @staticmethod
    def create_v2_tables(connection) -> bool:
        cursor = connection.cursor()
        try:
            logger.info("创建 subreddits 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS subreddits (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    daily_hot_post_ids JSONB DEFAULT '[]'::jsonb,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_fetched_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_subreddits_name ON subreddits(name);
                CREATE INDEX IF NOT EXISTS idx_subreddits_is_active ON subreddits(is_active);
                CREATE INDEX IF NOT EXISTS idx_subreddits_last_fetched ON subreddits(last_fetched_at);
                """
            )
            logger.info("创建 reddit_posts 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reddit_posts (
                    id VARCHAR(50) PRIMARY KEY,
                    subreddit_id INTEGER REFERENCES subreddits(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    url TEXT,
                    num_comments INTEGER DEFAULT 0,
                    score INTEGER DEFAULT 0,
                    created_utc TIMESTAMP,
                    selftext TEXT,
                    over_18 BOOLEAN DEFAULT FALSE,
                    gpt_summary TEXT,
                    gpt_summary_en TEXT,
                    gpt_processed_at TIMESTAMP,
                    gpt_error TEXT,
                    fetch_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_subreddit_id ON reddit_posts(subreddit_id);
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_fetch_date ON reddit_posts(fetch_date);
                CREATE INDEX IF NOT EXISTS idx_reddit_posts_score ON reddit_posts(score);
                """
            )
            logger.info("创建 users 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    language VARCHAR(10) DEFAULT 'zh-CN',
                    subscribed_subreddits JSONB DEFAULT '[]'::jsonb,
                    frequency VARCHAR(20) DEFAULT 'daily',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
                """
            )
            logger.info("创建 user_newsletter_logs 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_newsletter_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    posts_count INTEGER DEFAULT 0,
                    subreddits_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_user_newsletter_logs_user_id ON user_newsletter_logs(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_newsletter_logs_sent_at ON user_newsletter_logs(sent_at);
                """
            )
            connection.commit()
            logger.info("✅ V2 数据库表创建成功！")
            return True
        except Exception as e:
            connection.rollback()
            logger.error(f"❌ 创建表失败: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def insert_default_subreddits(connection) -> bool:
        try:
            cursor = connection.cursor()
            default_subreddits = [
                ('programming', 'Programming discussions'),
                ('python', 'Python programming'),
                ('machinelearning', 'Machine Learning'),
                ('technology', 'Technology news'),
                ('science', 'Science discussions'),
                ('worldnews', 'World news'),
                ('news', 'Current news'),
                ('todayilearned', 'TIL facts'),
            ]
            for name, description in default_subreddits:
                cursor.execute(
                    """
                    INSERT INTO subreddits (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (name, description),
                )
            connection.commit()
            cursor.close()
            logger.info(f"✅ 插入 {len(default_subreddits)} 个默认 subreddit")
            return True
        except Exception as e:
            logger.error(f"❌ 插入默认subreddit失败: {e}")
            connection.rollback()
            return False

    @staticmethod
    def upgrade_database(connection) -> bool:
        logger.info("🚀 开始升级数据库到 V2...")
        if not DatabaseSchemaV2.create_v2_tables(connection):
            return False
        if not DatabaseSchemaV2.insert_default_subreddits(connection):
            return False
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES ('schema_version', '2.0', CURRENT_TIMESTAMP)
                ON CONFLICT (key) 
                DO UPDATE SET value = '2.0', updated_at = CURRENT_TIMESTAMP
                """
            )
            connection.commit()
            cursor.close()
        except Exception as e:
            logger.warning(f"⚠️ 无法记录版本信息（settings表可能不存在）: {e}")
        logger.info("✅ 数据库升级到 V2 完成！")
        return True

    @staticmethod
    def get_schema_version(connection) -> Optional[str]:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception:
            return None

    @staticmethod
    def rollback_to_v1(connection) -> bool:
        try:
            cursor = connection.cursor()
            logger.warning("⚠️ 开始回滚数据库到 V1，将删除所有V2表...")
            tables_to_drop = ["user_newsletter_logs", "reddit_posts", "subreddits", "users"]
            for table in tables_to_drop:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                logger.info(f"✓ 删除表 {table}")
            try:
                cursor.execute(
                    """
                    UPDATE settings 
                    SET value = '1.0', updated_at = CURRENT_TIMESTAMP
                    WHERE key = 'schema_version'
                    """
                )
            except Exception:
                logger.warning("⚠️ 无法更新版本号（settings表可能不存在）")
            connection.commit()
            cursor.close()
            logger.info("✅ 数据库回滚到 V1 完成")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库回滚失败: {e}")
            connection.rollback()
            return False
