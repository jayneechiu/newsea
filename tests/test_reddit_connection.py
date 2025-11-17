"""
Reddit API连接测试模块
用于测试PRAW库与Reddit API的连接和认证
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import praw
from dotenv import load_dotenv


class RedditConnectionTest:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        self.reddit = None

    def test_connection(self):
        """测试Reddit API连接"""
        try:
            print("🔍 测试Reddit API连接...")

            # 创建Reddit实例
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
            )

            # 测试认证
            current_user = self.reddit.user.me()
            print(f"✅ Reddit API连接成功")
            print(f"当前登录用户: {current_user}")

            # 测试获取热门帖子
            print("\n📑 测试获取热门帖子...")
            subreddit = self.reddit.subreddit("AskReddit")
            posts = list(subreddit.hot(limit=3))

            print(f"✅ 成功获取 {len(posts)} 个热门帖子:")
            for i, post in enumerate(posts, 1):
                print(f"  {i}. {post.title[:60]}...")

            return True

        except Exception as e:
            print(f"❌ Reddit API连接失败: {e}")
            print("\n💡 请检查:")
            print("   - Reddit API凭据是否正确")
            print("   - .env文件是否存在且配置正确")
            print("   - 网络连接是否正常")
            return False


def main():
    """主测试函数"""
    test = RedditConnectionTest()
    success = test.test_connection()
    return success


if __name__ == "__main__":
    main()
