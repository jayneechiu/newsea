"""
数据库功能测试模块
用于测试SQLite数据库的连接和操作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from datetime import datetime
from src.database_manager import DatabaseManager
from src.config_manager import ConfigManager

class DatabaseTest:
    def __init__(self):
        self.config = ConfigManager()
        self.db_path = self.config.get_database_path()
        self.db_manager = None
    
    def test_database_connection(self):
        """测试数据库连接"""
        print("🔍 测试数据库连接...")
        
        try:
            self.db_manager = DatabaseManager(self.db_path)
            print("✅ 数据库连接成功")
            print(f"数据库路径: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def test_database_operations(self):
        """测试数据库基本操作"""
        print("\n🔍 测试数据库操作...")
        
        try:
            # 测试插入和标记帖子
            test_posts = [
                {
                    'id': 'test_post_1',
                    'title': '测试帖子1',
                    'author': 'test_user',
                    'url': 'https://reddit.com/test1',
                    'permalink': '/r/test/comments/test1/',
                    'subreddit': 'test',
                    'score': 100,
                    'num_comments': 10,
                    'created_utc': datetime.now().timestamp(),
                    'selftext': '测试内容1',
                    'is_video': False,
                    'over_18': False
                },
                {
                    'id': 'test_post_2',
                    'title': '测试帖子2',
                    'author': 'test_user',
                    'url': 'https://reddit.com/test2',
                    'permalink': '/r/test/comments/test2/',
                    'subreddit': 'test',
                    'score': 200,
                    'num_comments': 20,
                    'created_utc': datetime.now().timestamp(),
                    'selftext': '测试内容2',
                    'is_video': False,
                    'over_18': False
                }
            ]
            
            # 插入并标记测试帖子
            print("测试插入并标记帖子...")
            self.db_manager.mark_posts_as_sent(test_posts)
            print("✅ 帖子插入和标记成功")
            
            # 记录发送
            print("测试记录发送...")
            self.db_manager.log_newsletter_send(
                posts_count=len(test_posts),
                success=True,
                recipients=['test@example.com']
            )
            print("✅ 发送记录成功")
            
            # 获取统计信息
            print("测试获取统计信息...")
            stats = self.db_manager.get_newsletter_stats()
            print(f"✅ 统计信息获取成功: {stats}")
            
            # 清理测试数据
            print("清理测试数据...")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM posts WHERE id LIKE 'test_post_%'")
                conn.commit()
            print("✅ 测试数据清理完成")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库操作失败: {e}")
            return False
    
    def test_database_schema(self):
        """测试数据库表结构"""
        print("\n🔍 测试数据库表结构...")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查posts表
                cursor.execute("PRAGMA table_info(posts)")
                posts_columns = cursor.fetchall()
                expected_posts_columns = ['id', 'title', 'subreddit', 'score', 'url', 'created_utc', 'sent_at']
                
                actual_columns = [col[1] for col in posts_columns]
                for expected in expected_posts_columns:
                    if expected not in actual_columns:
                        print(f"❌ posts表缺少列: {expected}")
                        return False
                
                print("✅ posts表结构正确")
                
                # 检查newsletter_logs表
                cursor.execute("PRAGMA table_info(newsletter_logs)")
                logs_columns = cursor.fetchall()
                expected_logs_columns = ['id', 'sent_at', 'posts_count', 'success', 'error_message', 'recipients']
                
                actual_columns = [col[1] for col in logs_columns]
                for expected in expected_logs_columns:
                    if expected not in actual_columns:
                        print(f"❌ newsletter_logs表缺少列: {expected}")
                        return False
                
                print("✅ newsletter_logs表结构正确")
                return True
                
        except Exception as e:
            print(f"❌ 数据库表结构检查失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有数据库测试"""
        print("=" * 60)
        print("🗃️ 数据库功能测试")
        print("=" * 60)
        
        results = []
        
        # 测试1: 数据库连接
        results.append(self.test_database_connection())
        
        # 测试2: 数据库表结构
        if results[-1]:  # 只有连接成功才进行后续测试
            results.append(self.test_database_schema())
            
            # 测试3: 数据库操作
            if results[-1]:  # 只有表结构正确才进行操作测试
                results.append(self.test_database_operations())
        
        # 结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        success_count = sum(results)
        total_tests = len(results)
        
        print(f"通过测试: {success_count}/{total_tests}")
        print(f"成功率: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("🎉 所有数据库测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查数据库配置")
        
        return success_count == total_tests

def main():
    """主测试函数"""
    test = DatabaseTest()
    success = test.run_all_tests()
    return success

if __name__ == "__main__":
    main()
