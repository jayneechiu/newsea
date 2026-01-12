"""
数据库升级工具 - 执行 Schema V2 升级
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from backend.scraper.database_manager import DatabaseManager
from backend.scraper.database_schema_v2 import DatabaseSchemaV2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    print("=" * 60)
    print("📦 Reddit Newsletter Bot - 数据库升级工具")
    print("=" * 60)
    print()

    try:
        # 连接数据库
        print("🔌 正在连接数据库...")
        db = DatabaseManager()
        print("✅ 数据库连接成功")
        print()

        # 检查当前版本
        current_version = DatabaseSchemaV2.get_schema_version(db.connection)
        print(f"📌 当前数据库版本: {current_version or '1.0 (未设置)'}")
        print()

        # 确认升级
        print("⚠️  即将升级到 Schema V2 - 精简版用户定制化Newsletter系统")
        print()
        print("V2 核心功能：")
        print("  ✅ Subreddit管理和热帖缓存")
        print("  ✅ 帖子GPT摘要存储")
        print("  ✅ 用户订阅管理（含订阅列表）")
        print("  ✅ Newsletter发送日志")
        print()
        print("新增数据表（4个）：")
        print("  📊 subreddits - Subreddit主表（含daily_hot_post_ids缓存）")
        print("  📝 reddit_posts - 帖子表（含GPT摘要）")
        print("  👤 users - 用户表（含订阅列表和频率）")
        print("  📨 user_newsletter_logs - 发送日志表")
        print()

        response = input("❓ 确认要升级吗？(yes/no): ").strip().lower()
        
        if response not in ["yes", "y"]:
            print("❌ 取消升级")
            return

        print()
        print("🚀 开始升级...")
        print("-" * 60)

        # 执行升级
        success = DatabaseSchemaV2.upgrade_database(db.connection)

        print("-" * 60)
        
        if success:
            print()
            print("🎉 数据库升级成功！")
            print()
            print("📋 下一步：")
            print("  1. 查看文档: docs/database_schema_v2.md")
            print("  2. 开发用户管理模块: src/user_manager.py")
            print("  3. 开发个性化Newsletter: src/personalized_newsletter.py")
            print()
            
            # 显示统计信息
            cursor = db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM subreddits")
            subreddit_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM reddit_posts")
            post_count = cursor.fetchone()[0]
            cursor.close()
            
            print(f"📊 当前状态:")
            print(f"  • 用户数: {user_count}")
            print(f"  • Subreddit数: {subreddit_count}")
            print(f"  • 帖子数: {post_count}")
            print()
        else:
            print()
            print("❌ 数据库升级失败，请查看日志")
            print()
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ 错误: {e}")
        logger.exception("升级过程中发生错误")
        sys.exit(1)


def rollback():
    """回滚到 V1"""
    print("=" * 60)
    print("⚠️  数据库回滚工具 - 回滚到 V1")
    print("=" * 60)
    print()
    
    print("🚨 警告：这将删除所有 V2 新增的表和数据！")
    print()
    print("将删除的表（4个）：")
    print("  • user_newsletter_logs - Newsletter发送日志")
    print("  • users - 用户表（含订阅信息）")
    print("  • reddit_posts - 帖子表（含GPT摘要）")
    print("  • subreddits - Subreddit主表")
    print()

    response = input("❓ 确认要回滚吗？请输入 'DELETE ALL DATA' 确认: ").strip()
    
    if response != "DELETE ALL DATA":
        print("❌ 取消回滚")
        return

    try:
        print()
        print("🔌 正在连接数据库...")
        db = DatabaseManager()
        print("✅ 数据库连接成功")
        print()

        print("🔄 开始回滚...")
        success = DatabaseSchemaV2.rollback_to_v1(db.connection)

        if success:
            print()
            print("✅ 回滚成功！数据库已恢复到 V1")
            print()
        else:
            print()
            print("❌ 回滚失败，请查看日志")
            sys.exit(1)

    except Exception as e:
        print()
        print(f"❌ 错误: {e}")
        logger.exception("回滚过程中发生错误")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        main()
