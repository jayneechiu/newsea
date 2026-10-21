"""测试评论精选功能"""

import sys
import os
# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from backend.scraper.config_manager import ConfigManager
from backend.scraper.reddit_scraper import RedditScraper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_comment_curation():
    """测试评论获取和总结功能"""
    try:
        logger.info("开始测试评论精选功能...")

        # 初始化配置和Reddit爬虫
        config = ConfigManager()
        scraper = RedditScraper(config)

        # 获取热门帖子（包含评论）
        logger.info("正在抓取热门帖子及评论...")
        posts = scraper.get_hot_posts(limit=3)  # 只获取3个帖子进行测试

        if not posts:
            logger.error("未能获取到帖子")
            return

        logger.info(f"\n成功获取 {len(posts)} 个帖子\n")

        # 显示每个帖子的信息
        for i, post in enumerate(posts, 1):
            logger.info(f"{'='*60}")
            logger.info(f"帖子 #{i}: {post['title']}")
            logger.info(f"来源: r/{post['subreddit']}")
            logger.info(f"评分: {post['score']} | 评论数: {post['num_comments']}")

            # 显示GPT摘要
            if post.get("gpt_summary"):
                logger.info(f"\n📝 GPT摘要:\n{post['gpt_summary']}")

            # 显示原始评论
            if post.get("top_comments"):
                logger.info(f"\n💬 获取到 {len(post['top_comments'])} 条评论:")
                for j, comment in enumerate(post["top_comments"], 1):
                    logger.info(f"\n  评论 {j} (👍 {comment['score']}):")
                    logger.info(f"  作者: {comment['author']}")
                    logger.info(f"  内容: {comment['body'][:100]}...")

            # 显示评论摘要
            if post.get("comment_summary"):
                logger.info(f"\n✨ 评论精选摘要:\n{post['comment_summary']}")
            else:
                logger.info("\n⚠️ 未生成评论摘要")

            logger.info(f"{'='*60}\n")

        logger.info("✅ 测试完成！")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    test_comment_curation()
