"""
Reddit Scraper - Reddit API集成模块
"""

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
        
    def _initialize_reddit_client(self):
        """初始化Reddit客户端"""
        try:
            reddit = praw.Reddit(
                client_id=self.config.get_reddit_client_id(),
                client_secret=self.config.get_reddit_client_secret(),
                user_agent=self.config.get_reddit_user_agent(),
                username=self.config.get_reddit_username(),
                password=self.config.get_reddit_password()
            )
            
            # 测试连接
            reddit.user.me()
            logger.info("Reddit API连接成功")
            return reddit
            
        except Exception as e:
            logger.error(f"Reddit API连接失败: {e}")
            raise
    
    def get_hot_posts(self, limit: int = None) -> List[Dict]:
        """
        获取热门帖子
        
        Args:
            limit: 获取帖子数量限制
            
        Returns:
            帖子列表
        """
        try:
            limit = limit or self.config.get_posts_limit()
            subreddits = self.config.get_target_subreddits()
            all_posts = []
            
            for subreddit_name in subreddits:
                logger.info(f"正在抓取 r/{subreddit_name} 的热门帖子...")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=limit)
                
                for post in posts:
                    # 只获取最近24小时的帖子
                    post_time = datetime.fromtimestamp(post.created_utc)
                    if datetime.now() - post_time <= timedelta(hours=24):
                        post_data = {
                            'id': post.id,
                            'title': post.title,
                            'author': str(post.author),
                            'url': post.url,
                            'permalink': f"https://reddit.com{post.permalink}",
                            'subreddit': subreddit_name,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': post.created_utc,
                            'selftext': post.selftext[:500] if post.selftext else "",  # 限制长度
                            'is_video': post.is_video,
                            'over_18': post.over_18
                        }
                        all_posts.append(post_data)
            
            # 按分数排序
            all_posts.sort(key=lambda x: x['score'], reverse=True)
            
            # 过滤NSFW内容（如果配置中禁用）
            if not self.config.get_include_nsfw():
                all_posts = [post for post in all_posts if not post['over_18']]
            
            logger.info(f"共抓取到 {len(all_posts)} 个热门帖子")
            return all_posts[:self.config.get_newsletter_posts_limit()]
            
        except Exception as e:
            logger.error(f"抓取Reddit帖子时出错: {e}")
            return []
    
    def get_trending_posts(self, time_filter: str = 'day') -> List[Dict]:
        """
        获取趋势帖子
        
        Args:
            time_filter: 时间过滤器 ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            帖子列表
        """
        try:
            subreddits = self.config.get_target_subreddits()
            all_posts = []
            
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.top(time_filter=time_filter, limit=self.config.get_posts_limit())
                
                for post in posts:
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'author': str(post.author),
                        'url': post.url,
                        'permalink': f"https://reddit.com{post.permalink}",
                        'subreddit': subreddit_name,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'selftext': post.selftext[:500] if post.selftext else "",
                        'is_video': post.is_video,
                        'over_18': post.over_18
                    }
                    all_posts.append(post_data)
            
            all_posts.sort(key=lambda x: x['score'], reverse=True)
            
            if not self.config.get_include_nsfw():
                all_posts = [post for post in all_posts if not post['over_18']]
            
            return all_posts[:self.config.get_newsletter_posts_limit()]
            
        except Exception as e:
            logger.error(f"获取趋势帖子时出错: {e}")
            return []
