#!/usr/bin/env python3
"""Reddit Newsletter Bot - CLI管理工具"""

import sys
import os
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigManager
from src.reddit_scraper import RedditScraper
from src.newsletter_sender import NewsletterSender
from src.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_config():
    """验证配置是否正确"""
    print("🔧 验证配置...")
    
    try:
        config = ConfigManager()
        
        # 检查Reddit配置
        required_reddit = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
        missing_reddit = [key for key in required_reddit if not os.getenv(key)]
        
        if missing_reddit:
            print(f"❌ Reddit配置缺失: {', '.join(missing_reddit)}")
            return False
        
        # 检查SMTP配置
        required_smtp = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_RECIPIENTS']
        missing_smtp = [key for key in required_smtp if not os.getenv(key)]
        
        if missing_smtp:
            print(f"❌ SMTP配置缺失: {', '.join(missing_smtp)}")
            return False
            
        # 检查OpenAI配置
        if config.get_enable_gpt_summaries() and not config.get_openai_api_key():
            print("❌ OpenAI配置缺失: OPENAI_API_KEY")
            return False
        
        print("✅ 配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def test_reddit():
    """测试Reddit连接"""
    print("🔗 测试Reddit连接...")
    
    try:
        config = ConfigManager()
        scraper = RedditScraper(config)
        posts = scraper.get_hot_posts(limit=1)
        
        if posts:
            print(f"✅ Reddit连接成功，获取到 {len(posts)} 个帖子")
            print(f"示例帖子: {posts[0]['title'][:50]}...")
            return True
        else:
            print("❌ Reddit连接失败，未获取到帖子")
            return False
            
    except Exception as e:
        print(f"❌ Reddit连接测试失败: {e}")
        return False

def test_email():
    """测试邮件发送"""
    print("📧 测试邮件发送...")
    
    try:
        config = ConfigManager()
        sender = NewsletterSender(config)
        
        # 发送测试邮件
        test_posts = [{
            'title': '测试邮件 - Reddit Newsletter Bot',
            'url': 'https://example.com',
            'permalink': 'https://reddit.com/r/test',
            'subreddit': 'test',
            'score': 100,
            'author': 'testuser',
            'num_comments': 10,
            'gpt_summary': '这是一个测试帖子，用于验证邮件发送功能。'
        }]
        
        success, editor_words = sender.send_newsletter(test_posts)
        
        if success:
            print("✅ 邮件发送测试成功")
            return True
        else:
            print("❌ 邮件发送测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送测试失败: {e}")
        return False

def test_all():
    """运行完整测试"""
    print("🧪 运行完整系统测试...\n")
    
    results = []
    
    # 1. 配置验证
    results.append(("配置验证", validate_config()))
    
    # 2. Reddit连接测试
    results.append(("Reddit连接", test_reddit()))
    
    # 3. 邮件发送测试
    results.append(("邮件发送", test_email()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n总体状态: {'✅ 所有测试通过' if all_passed else '❌ 存在测试失败'}")
    
    return all_passed

def send_now():
    """立即发送Newsletter"""
    print("📬 立即发送Newsletter...")
    
    try:
        from main import RedditNewsletterBot
        
        bot = RedditNewsletterBot()
        bot.run_daily_newsletter()
        
        print("✅ Newsletter发送任务完成")
        
    except Exception as e:
        print(f"❌ Newsletter发送失败: {e}")

def clear_history():
    """清空数据库历史记录"""
    print("🗑️ 清空数据库历史记录...")
    
    try:
        config = ConfigManager()
        db = DatabaseManager()  # PostgreSQL 版本不需要路径参数
        
        # 确认操作
        response = input("⚠️ 这将删除所有历史记录，确定要继续吗？(输入 'YES' 确认): ")
        
        if response != 'YES':
            print("❌ 操作已取消")
            return False
        
        # 清空历史
        success = db.clear_all_history()
        
        if success:
            print("✅ 数据库历史记录已清空")
            return True
        else:
            print("❌ 清空历史记录失败")
            return False
            
    except Exception as e:
        print(f"❌ 清空历史记录失败: {e}")
        return False

def show_stats():
    """显示统计信息"""
    print("📈 Newsletter统计信息...")
    
    try:
        config = ConfigManager()
        db = DatabaseManager()  # PostgreSQL 版本不需要路径参数
        
        # 获取统计信息
        history = db.get_newsletter_history(limit=10)
        posts_count = db.get_total_posts_count()
        
        print(f"📊 总发送帖子数: {posts_count}")
        print(f"📧 最近发送记录 (最近10次):")
        print("-" * 80)
        
        for record in history:
            send_time = datetime.fromisoformat(record['sent_at'])
            status = "✅ 成功" if record['success'] else "❌ 失败"
            post_count = record['posts_count']
            recipients = record['recipients'] if isinstance(record['recipients'], list) else []
            
            print(f"{send_time.strftime('%Y-%m-%d %H:%M')} | {status} | {post_count}篇帖子 | {len(recipients)}位收件人")
        
        if not history:
            print("暂无发送记录")
            
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="Reddit Newsletter Bot 管理工具")
    
    parser.add_argument('command', choices=[
        'validate-config', 'test-reddit', 'test-email', 'test-all', 
        'send-now', 'stats', 'clear-history'
    ], help='要执行的命令')
    
    args = parser.parse_args()
    
    command_map = {
        'validate-config': validate_config,
        'test-reddit': test_reddit,
        'test-email': test_email,
        'test-all': test_all,
        'send-now': send_now,
        'stats': show_stats,
        'clear-history': clear_history,
    }
    
    try:
        command_map[args.command]()
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

if __name__ == "__main__":
    main()
