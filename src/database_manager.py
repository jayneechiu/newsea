"""
Database Manager - 数据库管理模块
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建帖子表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        author TEXT,
                        url TEXT,
                        permalink TEXT,
                        subreddit TEXT,
                        score INTEGER,
                        num_comments INTEGER,
                        created_utc REAL,
                        selftext TEXT,
                        is_video BOOLEAN,
                        over_18 BOOLEAN,
                        sent_at TIMESTAMP,
                        data_json TEXT
                    )
                ''')
                
                # 创建发送记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS newsletter_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        posts_count INTEGER,
                        success BOOLEAN,
                        error_message TEXT,
                        recipients TEXT
                    )
                ''')
                
                # 创建配置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("数据库初始化成功")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def filter_new_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        过滤出未发送过的新帖子
        
        Args:
            posts: 帖子列表
            
        Returns:
            新帖子列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                new_posts = []
                for post in posts:
                    cursor.execute('SELECT id FROM posts WHERE id = ?', (post['id'],))
                    if not cursor.fetchone():
                        new_posts.append(post)
                
                logger.info(f"筛选出 {len(new_posts)} 个新帖子（总共 {len(posts)} 个）")
                return new_posts
                
        except Exception as e:
            logger.error(f"过滤新帖子时出错: {e}")
            return posts  # 出错时返回所有帖子
    
    def mark_posts_as_sent(self, posts: List[Dict]) -> bool:
        """
        标记帖子为已发送
        
        Args:
            posts: 帖子列表
            
        Returns:
            操作是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sent_time = datetime.now()
                
                for post in posts:
                    cursor.execute('''
                        INSERT OR REPLACE INTO posts 
                        (id, title, author, url, permalink, subreddit, score, 
                         num_comments, created_utc, selftext, is_video, over_18, 
                         sent_at, data_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post['id'], post['title'], post['author'], post['url'],
                        post['permalink'], post['subreddit'], post['score'],
                        post['num_comments'], post['created_utc'], post['selftext'],
                        post['is_video'], post['over_18'], sent_time,
                        json.dumps(post, ensure_ascii=False)
                    ))
                
                conn.commit()
                logger.info(f"已标记 {len(posts)} 个帖子为已发送")
                return True
                
        except Exception as e:
            logger.error(f"标记帖子为已发送时出错: {e}")
            return False
    
    def log_newsletter_send(self, posts_count: int, success: bool, 
                           error_message: str = None, recipients: List[str] = None) -> bool:
        """
        记录Newsletter发送日志
        
        Args:
            posts_count: 帖子数量
            success: 是否成功
            error_message: 错误信息
            recipients: 收件人列表
            
        Returns:
            操作是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO newsletter_logs 
                    (posts_count, success, error_message, recipients)
                    VALUES (?, ?, ?, ?)
                ''', (
                    posts_count, success, error_message,
                    json.dumps(recipients) if recipients else None
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"记录Newsletter发送日志时出错: {e}")
            return False
    
    def get_recent_posts(self, days: int = 7) -> List[Dict]:
        """
        获取最近几天发送的帖子
        
        Args:
            days: 天数
            
        Returns:
            帖子列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM posts 
                    WHERE sent_at >= datetime('now', '-{} days')
                    ORDER BY sent_at DESC
                '''.format(days))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                posts = []
                for row in rows:
                    post_dict = dict(zip(columns, row))
                    if post_dict['data_json']:
                        post_dict.update(json.loads(post_dict['data_json']))
                    posts.append(post_dict)
                
                return posts
                
        except Exception as e:
            logger.error(f"获取最近帖子时出错: {e}")
            return []
    
    def get_newsletter_stats(self, days: int = 30) -> Dict:
        """
        获取Newsletter统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总发送次数
                cursor.execute('''
                    SELECT COUNT(*) FROM newsletter_logs 
                    WHERE sent_at >= datetime('now', '-{} days')
                '''.format(days))
                total_sends = cursor.fetchone()[0]
                
                # 成功发送次数
                cursor.execute('''
                    SELECT COUNT(*) FROM newsletter_logs 
                    WHERE sent_at >= datetime('now', '-{} days') AND success = 1
                '''.format(days))
                successful_sends = cursor.fetchone()[0]
                
                # 总帖子数
                cursor.execute('''
                    SELECT COUNT(*) FROM posts 
                    WHERE sent_at >= datetime('now', '-{} days')
                '''.format(days))
                total_posts = cursor.fetchone()[0]
                
                # 最后发送时间
                cursor.execute('''
                    SELECT MAX(sent_at) FROM newsletter_logs 
                    WHERE success = 1
                ''')
                last_send = cursor.fetchone()[0]
                
                return {
                    'total_sends': total_sends,
                    'successful_sends': successful_sends,
                    'success_rate': successful_sends / total_sends if total_sends > 0 else 0,
                    'total_posts': total_posts,
                    'last_send': last_send,
                    'days': days
                }
                
        except Exception as e:
            logger.error(f"获取Newsletter统计信息时出错: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 90):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除旧帖子记录
                cursor.execute('''
                    DELETE FROM posts 
                    WHERE sent_at < datetime('now', '-{} days')
                '''.format(days))
                deleted_posts = cursor.rowcount
                
                # 删除旧日志记录
                cursor.execute('''
                    DELETE FROM newsletter_logs 
                    WHERE sent_at < datetime('now', '-{} days')
                '''.format(days))
                deleted_logs = cursor.rowcount
                
                conn.commit()
                logger.info(f"清理完成：删除了 {deleted_posts} 个帖子记录和 {deleted_logs} 个日志记录")
                
        except Exception as e:
            logger.error(f"清理旧数据时出错: {e}")
    
    def close(self):
        """关闭数据库连接"""
        # SQLite连接会自动关闭，这里只是为了接口完整性
        pass
