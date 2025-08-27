#!/usr/bin/env python3
"""
Reddit Newsletter Bot - Main Entry Point
自动抓取Reddit热门帖子并发送Newsletter的定时服务
"""

import schedule
import time
import logging
from datetime import datetime
from src.reddit_scraper import RedditScraper
from src.newsletter_sender import NewsletterSender
from src.database_manager import DatabaseManager
from src.config_manager import ConfigManager

# 配置日志
import os
os.makedirs('data/logs', exist_ok=True)  # 确保日志目录存在

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/reddit_newsletter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RedditNewsletterBot:
    """Reddit Newsletter Bot主类"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.db_manager = DatabaseManager(self.config.get_database_path())
        self.reddit_scraper = RedditScraper(self.config)
        self.newsletter_sender = NewsletterSender(self.config)
        
    def run_daily_newsletter(self):
        """执行每日Newsletter任务"""
        try:
            logger.info("开始执行每日Newsletter任务...")
            
            # 1. 抓取Reddit热门帖子
            logger.info("正在抓取Reddit热门帖子...")
            posts = self.reddit_scraper.get_hot_posts()
            
            if not posts:
                logger.warning("未找到新的热门帖子")
                return
                
            # 2. 过滤已发送的帖子
            new_posts = self.db_manager.filter_new_posts(posts)
            
            if not new_posts:
                logger.info("没有新的帖子需要发送")
                return
                
            # 3. 生成并发送Newsletter
            logger.info(f"准备发送Newsletter，包含{len(new_posts)}个新帖子")
            success = self.newsletter_sender.send_newsletter(new_posts)
            
            if success:
                # 4. 记录已发送的帖子
                self.db_manager.mark_posts_as_sent(new_posts)
                logger.info("Newsletter发送成功！")
            else:
                logger.error("Newsletter发送失败")
                
        except Exception as e:
            logger.error(f"执行Newsletter任务时出错: {e}")
    
    def run_scheduler(self):
        """运行定时调度器"""
        logger.info("Reddit Newsletter Bot启动成功")
        logger.info(f"已配置每日{self.config.get_schedule_time()}发送Newsletter")
        
        # 配置定时任务 - 每天指定时间执行
        schedule.every().day.at(self.config.get_schedule_time()).do(self.run_daily_newsletter)
        
        # 可选：添加测试命令，立即执行一次
        if self.config.get_run_immediately():
            logger.info("立即执行一次Newsletter任务进行测试...")
            self.run_daily_newsletter()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

def main():
    """主函数"""
    try:
        bot = RedditNewsletterBot()
        bot.run_scheduler()
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
