"""
Config Manager - 配置管理模块
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ConfigManager:
    def get_chatgpt_api_key(self) -> str:
        # 兼容 chatgpt_client.py，优先 CHATGPT_API_KEY，其次 OPENAI_API_KEY
        return os.getenv("CHATGPT_API_KEY", os.getenv("OPENAI_API_KEY", ""))

    """配置管理器"""

    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            # override=False: 不覆盖已存在的环境变量（Docker --env-file 传递的）
            load_dotenv(self.config_file, override=False)
            logger.info(f"Config file {self.config_file} loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}, using environment variables or defaults")

    def get_reddit_client_id(self) -> str:
        return os.getenv("REDDIT_CLIENT_ID", "")

    def get_reddit_client_secret(self) -> str:
        return os.getenv("REDDIT_CLIENT_SECRET", "")

    def get_reddit_user_agent(self) -> str:
        return os.getenv("REDDIT_USER_AGENT", "Reddit Newsletter Bot v1.0")

    def get_reddit_username(self) -> str:
        return os.getenv("REDDIT_USERNAME", "")

    def get_reddit_password(self) -> str:
        return os.getenv("REDDIT_PASSWORD", "")

    # 目标Subreddit配置
    def get_target_subreddits(self) -> List[str]:
        subreddits_str = os.getenv("TARGET_SUBREDDITS", "AskReddit,todayilearned,worldnews,technology,science")
        return [s.strip() for s in subreddits_str.split(",")]

    def get_posts_limit(self) -> int:
        return int(os.getenv("POSTS_LIMIT", "25"))

    def get_newsletter_posts_limit(self) -> int:
        return int(os.getenv("NEWSLETTER_POSTS_LIMIT", "10"))

    def get_include_nsfw(self) -> bool:
        return os.getenv("INCLUDE_NSFW", "false").lower() == "true"

    # SMTP邮件配置
    def get_smtp_server(self) -> str:
        return os.getenv("SMTP_SERVER", "smtp.gmail.com")

    def get_smtp_port(self) -> int:
        return int(os.getenv("SMTP_PORT", "587"))

    def get_smtp_use_tls(self) -> bool:
        return os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def get_smtp_use_ssl(self) -> bool:
        return os.getenv("SMTP_USE_SSL", "false").lower() == "true"

    def get_smtp_username(self) -> str:
        return os.getenv("SMTP_USERNAME", "")

    def get_smtp_password(self) -> str:
        return os.getenv("SMTP_PASSWORD", "")

    def get_smtp_from_email(self) -> str:
        return os.getenv("SMTP_FROM_EMAIL", self.get_smtp_username())

    def get_recipients(self) -> List[str]:
        recipients_str = os.getenv("EMAIL_RECIPIENTS", "")
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(",")]

    # 定时任务配置
    def get_schedule_time(self) -> str:
        return os.getenv("SCHEDULE_TIME", "09:00")

    def get_run_immediately(self) -> bool:
        return os.getenv("RUN_IMMEDIATELY", "false").lower() == "true"

    # PostgreSQL 数据库配置
    def get_database_config(self) -> Dict[str, Any]:
        """获取 PostgreSQL 数据库配置"""
        # 优先使用 DATABASE_URL (Azure PostgreSQL / Supabase 格式)
        database_url = os.getenv("DATABASE_URL")

        if database_url:
            # 解析 PostgreSQL URL
            parsed = urlparse(database_url)
            return {
                "host": parsed.hostname,
                "port": parsed.port or 5432,
                "database": parsed.path[1:] if parsed.path else "postgres",  # 移除开头的 '/'
                "user": parsed.username,
                "password": parsed.password,
                "sslmode": "require",
            }
        else:
            # 使用单独的环境变量
            return {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "reddit_newsletter"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "sslmode": os.getenv("DB_SSLMODE", "require"),
            }

    # GPT/OpenAI 配置
    def get_openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    def get_openai_api_base(self) -> str:
        return os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    def get_openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def get_enable_gpt_summaries(self) -> bool:
        return os.getenv("ENABLE_GPT_SUMMARIES", "true").lower() == "true"

    def get_enable_editor_summary(self) -> bool:
        return os.getenv("ENABLE_EDITOR_SUMMARY", "true").lower() == "true"

    # Newsletter 编辑配置
    def get_newsletter_editor_name(self) -> str:
        return os.getenv("NEWSLETTER_EDITOR_NAME", "Reddit Newsletter Team")

    def get_newsletter_title(self) -> str:
        return os.getenv("NEWSLETTER_TITLE", "Reddit 热门精选")

    # Web服务配置
    def get_web_host(self) -> str:
        return os.getenv("WEB_HOST", "127.0.0.1")

    def get_web_port(self) -> int:
        return int(os.getenv("WEB_PORT", "5000"))

    def get_web_debug(self) -> bool:
        return os.getenv("WEB_DEBUG", "false").lower() == "true"

    def get_web_secret_key(self) -> str:
        return os.getenv("WEB_SECRET_KEY", "dev-secret-key-change-in-production")

    def get_enable_web_service(self) -> bool:
        return os.getenv("ENABLE_WEB_SERVICE", "false").lower() == "true"

    # 验证配置
    def validate_config(self) -> bool:
        """验证必要的配置是否完整"""
        errors = []

        # 检查Reddit API配置
        if not self.get_reddit_client_id():
            errors.append("缺少 REDDIT_CLIENT_ID")
        if not self.get_reddit_client_secret():
            errors.append("缺少 REDDIT_CLIENT_SECRET")
        if not self.get_reddit_username():
            errors.append("缺少 REDDIT_USERNAME")
        if not self.get_reddit_password():
            errors.append("缺少 REDDIT_PASSWORD")

        # 检查SMTP配置
        if not self.get_smtp_username():
            errors.append("缺少 SMTP_USERNAME")
        if not self.get_smtp_password():
            errors.append("缺少 SMTP_PASSWORD")

        # 检查收件人配置
        if not self.get_recipients():
            errors.append("缺少 EMAIL_RECIPIENTS")

        # 检查 PostgreSQL 数据库配置
        db_config = self.get_database_config()
        if not db_config.get("host"):
            errors.append("缺少 PostgreSQL 主机配置 (DB_HOST 或 DATABASE_URL)")
        if not db_config.get("user"):
            errors.append("缺少 PostgreSQL 用户配置 (DB_USER 或 DATABASE_URL)")
        if not db_config.get("password"):
            errors.append("缺少 PostgreSQL 密码配置 (DB_PASSWORD 或 DATABASE_URL)")
        if not db_config.get("database"):
            errors.append("缺少 PostgreSQL 数据库名配置 (DB_NAME 或 DATABASE_URL)")

        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False

        logger.info("Configuration validation passed")
        return True

    def get_config_summary(self) -> dict:
        """获取配置摘要（隐藏敏感信息）"""
        db_config = self.get_database_config()

        return {
            "target_subreddits": self.get_target_subreddits(),
            "posts_limit": self.get_posts_limit(),
            "newsletter_posts_limit": self.get_newsletter_posts_limit(),
            "include_nsfw": self.get_include_nsfw(),
            "smtp_server": self.get_smtp_server(),
            "smtp_port": self.get_smtp_port(),
            "smtp_use_tls": self.get_smtp_use_tls(),
            "smtp_use_ssl": self.get_smtp_use_ssl(),
            "schedule_time": self.get_schedule_time(),
            "recipients_count": len(self.get_recipients()),
            "run_immediately": self.get_run_immediately(),
            "enable_gpt_summaries": self.get_enable_gpt_summaries(),
            "enable_editor_summary": self.get_enable_editor_summary(),
            "openai_model": self.get_openai_model(),
            "enable_web_service": self.get_enable_web_service(),
            "web_host": self.get_web_host(),
            "web_port": self.get_web_port(),
            "has_openai_key": bool(self.get_openai_api_key()),
            "database_type": "postgresql",
            "database_host": db_config.get("host", ""),
            "database_port": db_config.get("port", ""),
            "database_name": db_config.get("database", ""),
            "database_user": db_config.get("user", ""),
            "database_sslmode": db_config.get("sslmode", ""),
        }
