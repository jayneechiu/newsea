"""Reddit Scraper - Reddit API集成模块"""

import praw
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)


class RedditScraper:
    """Reddit帖子抓取器"""

    def __init__(self, config):
        self.config = config
        self.reddit = self._initialize_reddit_client()
        self.gpt_client = None
        if self.config.get_enable_gpt_summaries():
            from .chatgpt_client import ChatGPTClient

            self.gpt_client = ChatGPTClient(self.config)

    def _initialize_reddit_client(self):
        """初始化Reddit客户端"""
        try:
            reddit = praw.Reddit(
                client_id=self.config.get_reddit_client_id(),
                client_secret=self.config.get_reddit_client_secret(),
                user_agent=self.config.get_reddit_user_agent(),
                username=self.config.get_reddit_username(),
                password=self.config.get_reddit_password(),
            )

            reddit.user.me()
            logger.info("Reddit API connected successfully")
            return reddit

        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")
            raise

    def _get_top_comments(self, post, limit: int = 5) -> List[Dict]:
        """获取帖子的热门评论"""
        try:
            # 获取评论，按最佳排序
            post.comment_sort = "best"
            post.comments.replace_more(limit=0)  # 不展开"more comments"

            top_comments = []
            for comment in post.comments[:limit]:
                if hasattr(comment, "body") and comment.body != "[deleted]":
                    comment_data = {
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "body": comment.body[:300],  # 限制评论长度
                        "score": comment.score,
                        "created_utc": comment.created_utc,
                    }
                    top_comments.append(comment_data)

            logger.info(f"Retrieved {len(top_comments)} comments (post: {post.id})")
            return top_comments

        except Exception as e:
            logger.warning(f"Failed to get comments (post: {post.id}): {e}")
            return []

    def get_hot_posts(self, limit: int = None) -> List[Dict]:
        """获取热门帖子"""
        try:
            limit = limit or self.config.get_posts_limit()
            subreddits = self.config.get_target_subreddits()
            all_posts = []

            for subreddit_name in subreddits:
                logger.info(f"Scraping hot posts from r/{subreddit_name}...")
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=limit)

                for post in posts:
                    post_time = datetime.fromtimestamp(post.created_utc)
                    if datetime.now() - post_time <= timedelta(hours=24):
                        post_data = {
                            "id": post.id,
                            "title": post.title,
                            "author": str(post.author),
                            "url": post.url,
                            "permalink": f"https://reddit.com{post.permalink}",
                            "subreddit": subreddit_name,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "created_utc": post.created_utc,
                            "selftext": post.selftext[:500] if post.selftext else "",
                            "is_video": post.is_video,
                            "over_18": post.over_18,
                        }

                        # 获取热门评论
                        post_data["top_comments"] = self._get_top_comments(post)

                        if self.config.get_enable_gpt_summaries():
                            try:
                                post_data["gpt_summary"] = self.gpt_client.summarize_and_analyze(
                                    post.title, post_data["selftext"]
                                )
                                # 如果有评论，生成评论摘要
                                if post_data["top_comments"]:
                                    post_data["comment_summary"] = self.gpt_client.summarize_comments(
                                        post_data["top_comments"]
                                    )
                                else:
                                    post_data["comment_summary"] = ""
                            except Exception as e:
                                post_data["gpt_summary"] = f"[分析失败: {e}]"
                                post_data["comment_summary"] = ""
                        else:
                            post_data["gpt_summary"] = ""
                            post_data["comment_summary"] = ""

                        all_posts.append(post_data)

            all_posts.sort(key=lambda x: x["score"], reverse=True)
            if not self.config.get_include_nsfw():
                all_posts = [post for post in all_posts if not post["over_18"]]

            logger.info(f"共抓取到 {len(all_posts)} 个热门帖子")
            return all_posts[: self.config.get_newsletter_posts_limit()]

        except Exception as e:
            logger.error(f"抓取Reddit帖子时出错: {e}")
            return []

    def get_trending_posts(self, time_filter: str = "day") -> List[Dict]:
        """获取趋势帖子"""
        try:
            subreddits = self.config.get_target_subreddits()
            all_posts = []

            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.top(time_filter=time_filter, limit=self.config.get_posts_limit())

                for post in posts:
                    post_data = {
                        "id": post.id,
                        "title": post.title,
                        "author": str(post.author),
                        "url": post.url,
                        "permalink": f"https://reddit.com{post.permalink}",
                        "subreddit": subreddit_name,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created_utc": post.created_utc,
                        "selftext": post.selftext[:500] if post.selftext else "",
                        "is_video": post.is_video,
                        "over_18": post.over_18,
                    }

                    # 获取热门评论
                    post_data["top_comments"] = self._get_top_comments(post)

                    all_posts.append(post_data)

            all_posts.sort(key=lambda x: x["score"], reverse=True)
            if not self.config.get_include_nsfw():
                all_posts = [post for post in all_posts if not post["over_18"]]

            return all_posts[: self.config.get_newsletter_posts_limit()]

        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            return []
