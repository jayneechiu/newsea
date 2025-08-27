#!/usr/bin/env python3
"""
Reddit Newsletter Bot - 工具脚本
提供各种管理和测试功能
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.config_manager import ConfigManager
from src.reddit_scraper import RedditScraper
from src.newsletter_sender import NewsletterSender
from src.database_manager import DatabaseManager

# 配置日志
import os
# 获取项目根目录的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(project_root, 'data', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            os.path.join(logs_dir, 'reddit_newsletter.log'),
            encoding='utf-8'  # 支持中文字符
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_reddit_connection(config):
    """测试Reddit API连接"""
    try:
        logger.info("测试Reddit API连接...")
        scraper = RedditScraper(config)
        posts = scraper.get_hot_posts(limit=5)
        
        if posts:
            logger.info(f"Reddit API连接成功！获取到 {len(posts)} 个测试帖子:")
            for i, post in enumerate(posts, 1):
                logger.info(f"  {i}. {post['title']} (r/{post['subreddit']})")
        else:
            logger.warning("Reddit API连接成功，但未获取到帖子")
            
    except Exception as e:
        logger.error(f"Reddit API连接失败: {e}")

def test_email_sending(config):
    """测试邮件发送"""
    try:
        logger.info("测试邮件发送...")
        sender = NewsletterSender(config)
        
        success = sender.test_email_connection()
        
        if success:
            logger.info("测试邮件发送成功！")
        else:
            logger.error("测试邮件发送失败")
            
    except Exception as e:
        logger.error(f"测试邮件发送时出错: {e}")

def run_full_test(config):
    """运行完整测试"""
    logger.info("开始运行完整测试...")
    
    # 1. 测试Reddit连接
    test_reddit_connection(config)
    
    # 2. 测试邮件发送
    test_email_sending(config)
    
    # 3. 测试数据库
    try:
        logger.info("测试数据库连接...")
        db_manager = DatabaseManager(config.get_database_path())
        stats = db_manager.get_newsletter_stats()
        logger.info(f"数据库连接成功！统计信息: {stats}")
    except Exception as e:
        logger.error(f"数据库测试失败: {e}")

def send_newsletter_now(config):
    """立即发送一次Newsletter"""
    try:
        logger.info("立即发送Newsletter...")
        
        # 初始化组件
        db_manager = DatabaseManager(config.get_database_path())
        scraper = RedditScraper(config)
        sender = NewsletterSender(config)
        
        # 抓取帖子
        logger.info("抓取Reddit热门帖子...")
        posts = scraper.get_hot_posts()
        
        if not posts:
            logger.warning("未找到帖子")
            return
        
        # 过滤新帖子
        new_posts = db_manager.filter_new_posts(posts)
        
        if not new_posts:
            logger.info("没有新帖子需要发送")
            return
        
        # 发送Newsletter
        logger.info(f"准备发送Newsletter，包含 {len(new_posts)} 个帖子")
        success = sender.send_newsletter(new_posts)
        
        if success:
            db_manager.mark_posts_as_sent(new_posts)
            db_manager.log_newsletter_send(
                len(new_posts), True, None, config.get_recipients()
            )
            logger.info("Newsletter发送成功！")
        else:
            db_manager.log_newsletter_send(
                len(new_posts), False, "发送失败", config.get_recipients()
            )
            logger.error("Newsletter发送失败")
            
    except Exception as e:
        logger.error(f"发送Newsletter时出错: {e}")

def show_stats(config):
    """显示统计信息"""
    try:
        db_manager = DatabaseManager(config.get_database_path())
        stats = db_manager.get_newsletter_stats()
        
        print("\n=== Reddit Newsletter Bot 统计信息 ===")
        print(f"统计周期: 最近 {stats.get('days', 30)} 天")
        print(f"总发送次数: {stats.get('total_sends', 0)}")
        print(f"成功发送次数: {stats.get('successful_sends', 0)}")
        print(f"成功率: {stats.get('success_rate', 0):.2%}")
        print(f"总帖子数: {stats.get('total_posts', 0)}")
        print(f"最后发送时间: {stats.get('last_send', '从未发送')}")
        
        # 显示配置摘要
        config_summary = config.get_config_summary()
        print("\n=== 当前配置 ===")
        print(f"目标Subreddit: {', '.join(config_summary['target_subreddits'])}")
        print(f"每日发送时间: {config_summary['schedule_time']}")
        print(f"Newsletter帖子数量: {config_summary['newsletter_posts_limit']}")
        print(f"收件人数量: {config_summary['recipients_count']}")
        print(f"包含NSFW内容: {config_summary['include_nsfw']}")
        
    except Exception as e:
        logger.error(f"获取统计信息时出错: {e}")

def cleanup_database(config, days):
    """清理数据库"""
    try:
        logger.info(f"清理 {days} 天前的数据...")
        db_manager = DatabaseManager(config.get_database_path())
        db_manager.cleanup_old_data(days)
        logger.info("数据清理完成")
    except Exception as e:
        logger.error(f"清理数据时出错: {e}")

def validate_config(config):
    """验证配置"""
    logger.info("验证配置...")
    
    is_valid = config.validate_config()
    
    if is_valid:
        logger.info("✅ 配置验证通过")
        
        # 显示配置摘要
        summary = config.get_config_summary()
        print("\n=== 配置摘要 ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        logger.error("❌ 配置验证失败，请检查 .env 文件")

def main():
    parser = argparse.ArgumentParser(description='Reddit Newsletter Bot 工具脚本')
    parser.add_argument('command', choices=[
        'test-reddit', 'test-email', 'test-all', 'send-now', 
        'stats', 'cleanup', 'validate-config'
    ], help='要执行的命令')
    parser.add_argument('--days', type=int, default=90, help='清理数据的天数 (默认90天)')
    
    args = parser.parse_args()
    
    # 加载配置
    config = ConfigManager()
    
    # 执行相应命令
    if args.command == 'test-reddit':
        test_reddit_connection(config)
    elif args.command == 'test-email':
        test_email_sending(config)
    elif args.command == 'test-all':
        run_full_test(config)
    elif args.command == 'send-now':
        send_newsletter_now(config)
    elif args.command == 'stats':
        show_stats(config)
    elif args.command == 'cleanup':
        cleanup_database(config, args.days)
    elif args.command == 'validate-config':
        validate_config(config)

if __name__ == '__main__':
    main()
