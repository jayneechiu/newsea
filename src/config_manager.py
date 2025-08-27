"""
Config Manager - 配置管理模块
"""

import os
import logging
from typing import List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = '.env'):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            load_dotenv(self.config_file)
            logger.info(f"配置文件 {self.config_file} 加载成功")
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}，将使用默认配置")
    
    # Reddit API 配置
    def get_reddit_client_id(self) -> str:
        return os.getenv('REDDIT_CLIENT_ID', '')
    
    def get_reddit_client_secret(self) -> str:
        return os.getenv('REDDIT_CLIENT_SECRET', '')
    
    def get_reddit_user_agent(self) -> str:
        return os.getenv('REDDIT_USER_AGENT', 'Reddit Newsletter Bot v1.0')
    
    def get_reddit_username(self) -> str:
        return os.getenv('REDDIT_USERNAME', '')
    
    def get_reddit_password(self) -> str:
        return os.getenv('REDDIT_PASSWORD', '')
    
    # 目标Subreddit配置
    def get_target_subreddits(self) -> List[str]:
        subreddits_str = os.getenv('TARGET_SUBREDDITS', 'AskReddit,todayilearned,worldnews,technology,science')
        return [s.strip() for s in subreddits_str.split(',')]
    
    def get_posts_limit(self) -> int:
        return int(os.getenv('POSTS_LIMIT', '25'))
    
    def get_newsletter_posts_limit(self) -> int:
        return int(os.getenv('NEWSLETTER_POSTS_LIMIT', '10'))
    
    def get_include_nsfw(self) -> bool:
        return os.getenv('INCLUDE_NSFW', 'false').lower() == 'true'
    
    # SMTP邮件配置
    def get_smtp_server(self) -> str:
        return os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    
    def get_smtp_port(self) -> int:
        return int(os.getenv('SMTP_PORT', '587'))
    
    def get_smtp_use_tls(self) -> bool:
        return os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    def get_smtp_use_ssl(self) -> bool:
        return os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
    
    def get_smtp_username(self) -> str:
        return os.getenv('SMTP_USERNAME', '')
    
    def get_smtp_password(self) -> str:
        return os.getenv('SMTP_PASSWORD', '')
    
    def get_smtp_from_email(self) -> str:
        return os.getenv('SMTP_FROM_EMAIL', self.get_smtp_username())
    
    def get_recipients(self) -> List[str]:
        recipients_str = os.getenv('EMAIL_RECIPIENTS', '')
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(',')]
    
    # 定时任务配置
    def get_schedule_time(self) -> str:
        return os.getenv('SCHEDULE_TIME', '09:00')
    
    def get_run_immediately(self) -> bool:
        return os.getenv('RUN_IMMEDIATELY', 'false').lower() == 'true'
    
    # 数据库配置
    def get_database_path(self) -> str:
        default_path = 'data/database/reddit_newsletter.db'
        db_path = os.getenv('DATABASE_PATH', default_path)
        
        # 如果是相对路径，转换为基于项目根目录的绝对路径
        if not os.path.isabs(db_path):
            # 获取项目根目录（从src目录向上一级）
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, db_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return db_path
    
    # GPT/OpenAI 配置
    def get_openai_api_key(self) -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    def get_openai_api_base(self) -> str:
        return os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    def get_openai_model(self) -> str:
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    def get_enable_gpt_summaries(self) -> bool:
        return os.getenv('ENABLE_GPT_SUMMARIES', 'true').lower() == 'true'
    
    def get_enable_editor_summary(self) -> bool:
        return os.getenv('ENABLE_EDITOR_SUMMARY', 'true').lower() == 'true'
    
    # Web服务配置
    def get_web_host(self) -> str:
        return os.getenv('WEB_HOST', '127.0.0.1')
    
    def get_web_port(self) -> int:
        return int(os.getenv('WEB_PORT', '5000'))
    
    def get_web_debug(self) -> bool:
        return os.getenv('WEB_DEBUG', 'false').lower() == 'true'
    
    def get_web_secret_key(self) -> str:
        return os.getenv('WEB_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    def get_enable_web_service(self) -> bool:
        return os.getenv('ENABLE_WEB_SERVICE', 'false').lower() == 'true'
    
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
        
        if errors:
            logger.error("配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("配置验证通过")
        return True
    
    def get_config_summary(self) -> dict:
        """获取配置摘要（隐藏敏感信息）"""
        return {
            'target_subreddits': self.get_target_subreddits(),
            'posts_limit': self.get_posts_limit(),
            'newsletter_posts_limit': self.get_newsletter_posts_limit(),
            'include_nsfw': self.get_include_nsfw(),
            'smtp_server': self.get_smtp_server(),
            'smtp_port': self.get_smtp_port(),
            'smtp_use_tls': self.get_smtp_use_tls(),
            'smtp_use_ssl': self.get_smtp_use_ssl(),
            'schedule_time': self.get_schedule_time(),
            'recipients_count': len(self.get_recipients()),
            'database_path': self.get_database_path(),
            'run_immediately': self.get_run_immediately(),
            'enable_gpt_summaries': self.get_enable_gpt_summaries(),
            'enable_editor_summary': self.get_enable_editor_summary(),
            'openai_model': self.get_openai_model(),
            'enable_web_service': self.get_enable_web_service(),
            'web_host': self.get_web_host(),
            'web_port': self.get_web_port(),
            'has_openai_key': bool(self.get_openai_api_key())
        }
