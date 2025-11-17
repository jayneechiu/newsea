#!/usr/bin/env python3
"""Reddit Newsletter Bot - Enhanced Version with CLI Support"""

import sys
import os
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import RedditNewsletterBot
from src.config_manager import ConfigManager


def setup_logging():
    """设置日志配置"""
    os.makedirs("data/logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("data/logs/reddit_newsletter.log", encoding="utf-8"), logging.StreamHandler()],
    )


def run_once():
    """运行一次Newsletter发送"""
    print("🚀 启动Reddit Newsletter Bot (单次运行模式)")

    try:
        bot = RedditNewsletterBot()
        bot.run_daily_newsletter()
        print("✅ Newsletter任务完成")

    except Exception as e:
        print(f"❌ 运行失败: {e}")
        sys.exit(1)


def run_scheduler():
    """运行定时调度器"""
    print("🚀 启动Reddit Newsletter Bot (定时调度模式)")

    try:
        bot = RedditNewsletterBot()

        config = ConfigManager()
        if config.get_run_immediately():
            print("🔄 检测到立即运行配置，先执行一次...")
            bot.run_daily_newsletter()

        bot.run_scheduler()

    except KeyboardInterrupt:
        print("\n👋 Bot已停止运行")
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        sys.exit(1)


def show_help():
    """显示使用帮助"""
    help_text = """
Reddit Newsletter Bot - 使用指南
================================

运行模式:
  python enhanced_main.py                     # 定时调度模式
  python enhanced_main.py --once              # 单次运行模式
  python enhanced_main.py --help              # 显示帮助

管理工具:
  python tools.py validate-config             # 验证配置
  python tools.py test-reddit                 # 测试Reddit连接  
  python tools.py test-email                  # 测试邮件发送
  python tools.py test-all                    # 运行完整测试
  python tools.py send-now                    # 立即发送Newsletter
  python tools.py stats                       # 显示统计信息

配置文件:
  .env                                         # 主配置文件
  .env.example                                 # 配置模板文件

主要功能:
  ✅ 自动抓取Reddit热门帖子
  ✅ AI生成内容摘要和编辑寄语  
  ✅ 发送HTML邮件Newsletter
  ✅ 数据库记录历史信息
  ✅ 完整的测试和管理工具

更多信息请查看 README.md
    """
    print(help_text)


def main():
    parser = argparse.ArgumentParser(
        description="Reddit Newsletter Bot - Enhanced Version", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--once", action="store_true", help="运行一次Newsletter发送任务后退出")
    parser.add_argument("--help-extended", action="store_true", help="显示详细使用指南")

    args = parser.parse_args()

    setup_logging()

    if args.help_extended:
        show_help()
        return

    if args.once:
        run_once()
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
