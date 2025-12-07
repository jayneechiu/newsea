"""
PostgreSQL 数据库连接测试模块
用于测试 PostgreSQL 数据库连接和基本操作
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime
from scraper.config_manager import ConfigManager


class PostgreSQLConnectionTest:
    def __init__(self):
        self.config = ConfigManager()
        self.db_config = self.config.get_database_config()
        self.connection = None

    def test_basic_connection(self):
        """测试基础数据库连接"""
        print("🔍 测试 PostgreSQL 基础连接...")

        try:
            # 显示连接信息（隐藏密码）
            print(f"   主机: {self.db_config.get('host', 'N/A')}")
            print(f"   端口: {self.db_config.get('port', 'N/A')}")
            print(f"   数据库: {self.db_config.get('database', 'N/A')}")
            print(f"   用户: {self.db_config.get('user', 'N/A')}")
            print(f"   SSL模式: {self.db_config.get('sslmode', 'N/A')}")

            # 检查必要配置
            required_fields = ["host", "port", "database", "user", "password"]
            missing_fields = [field for field in required_fields if not self.db_config.get(field)]

            if missing_fields:
                print(f"❌ 缺少必要配置: {', '.join(missing_fields)}")
                return False

            # 尝试连接（增加重试机制）
            print("   正在尝试连接...")
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        print(f"   重试连接 ({attempt + 1}/{max_retries})...")

                    self.connection = psycopg2.connect(
                        host=self.db_config["host"],
                        port=self.db_config["port"],
                        database=self.db_config["database"],
                        user=self.db_config["user"],
                        password=self.db_config["password"],
                        sslmode=self.db_config.get("sslmode", "require"),
                        connect_timeout=15,  # 缩短超时时间
                    )

                    print("✅ PostgreSQL 连接成功")
                    return True

                except psycopg2.OperationalError as e:
                    if "timeout" in str(e).lower() or "connection" in str(e).lower():
                        if attempt < max_retries - 1:
                            print(f"   连接超时，正在重试...")
                            continue
                        else:
                            print(f"❌ 连接超时 (尝试了 {max_retries} 次)")
                            print("💡 建议:")
                            print("   1. 检查网络连接")
                            print("   2. 确认 Railway 数据库服务状态")
                            print("   3. 验证数据库主机地址和端口")
                            return False
                    else:
                        print(f"❌ PostgreSQL 连接失败: {e}")
                        return False

            return False

        except psycopg2.Error as e:
            print(f"❌ PostgreSQL 连接失败: {e}")
            print("💡 可能的解决方案:")
            print("   1. 检查 DATABASE_URL 或数据库配置")
            print("   2. 确认数据库用户名和密码")
            print("   3. 检查 Railway 数据库服务状态")
            return False
        except Exception as e:
            print(f"❌ 连接时发生未知错误: {e}")
            return False

    def test_database_version(self):
        """测试数据库版本查询"""
        print("🔍 测试数据库版本查询...")

        if not self.connection:
            print("❌ 需要先建立数据库连接")
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()

            print(f"✅ PostgreSQL 版本: {version.split(',')[0]}")
            return True

        except psycopg2.Error as e:
            print(f"❌ 查询数据库版本失败: {e}")
            return False

    def test_permissions(self):
        """测试数据库权限"""
        print("🔍 测试数据库权限...")

        if not self.connection:
            print("❌ 需要先建立数据库连接")
            return False

        try:
            cursor = self.connection.cursor()

            # 测试创建表权限
            test_table = "connection_test_table"
            cursor.execute(
                f"""
                DROP TABLE IF EXISTS {test_table};
                CREATE TABLE {test_table} (
                    id SERIAL PRIMARY KEY,
                    test_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            print("✅ 表创建权限正常")

            # 测试插入权限
            cursor.execute(
                f"""
                INSERT INTO {test_table} (test_message) 
                VALUES (%s);
            """,
                ("PostgreSQL 连接测试",),
            )
            print("✅ 数据插入权限正常")

            # 测试查询权限
            cursor.execute(f"SELECT COUNT(*) FROM {test_table};")
            count = cursor.fetchone()[0]
            print(f"✅ 数据查询权限正常，测试表中有 {count} 条记录")

            # 测试更新权限
            cursor.execute(
                f"""
                UPDATE {test_table} 
                SET test_message = %s 
                WHERE id = 1;
            """,
                ("PostgreSQL 连接测试 - 已更新",),
            )
            print("✅ 数据更新权限正常")

            # 测试删除权限
            cursor.execute(f"DELETE FROM {test_table} WHERE id = 1;")
            print("✅ 数据删除权限正常")

            # 清理测试表
            cursor.execute(f"DROP TABLE {test_table};")
            print("✅ 表删除权限正常")

            cursor.close()
            self.connection.commit()
            return True

        except psycopg2.Error as e:
            print(f"❌ 权限测试失败: {e}")
            return False

    def test_newsletter_tables_creation(self):
        """测试创建 Newsletter 相关表结构"""
        print("🔍 测试创建 Newsletter 表结构...")

        if not self.connection:
            print("❌ 需要先建立数据库连接")
            return False

        try:
            cursor = self.connection.cursor()

            # 创建帖子表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_posts (
                    id SERIAL PRIMARY KEY,
                    post_id VARCHAR(50) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    subreddit VARCHAR(100) NOT NULL,
                    score INTEGER NOT NULL,
                    created_utc TIMESTAMP NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    newsletter_date DATE NOT NULL
                )
            """
            )
            print("✅ sent_posts 表创建成功")

            # 创建统计表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS newsletter_stats (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE NOT NULL,
                    posts_sent INTEGER NOT NULL DEFAULT 0,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    avg_score DECIMAL(10,2) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            print("✅ newsletter_stats 表创建成功")

            # 创建索引
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sent_posts_post_id 
                ON sent_posts(post_id)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sent_posts_date 
                ON sent_posts(newsletter_date)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_newsletter_stats_date 
                ON newsletter_stats(date)
            """
            )
            print("✅ 数据库索引创建成功")

            # 测试插入数据
            test_date = datetime.now().date()
            cursor.execute(
                """
                INSERT INTO sent_posts 
                (post_id, title, url, author, subreddit, score, created_utc, newsletter_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (post_id) DO NOTHING
            """,
                (
                    "test_post_123",
                    "PostgreSQL 连接测试帖子",
                    "https://example.com/test",
                    "test_user",
                    "test_subreddit",
                    100,
                    datetime.now(),
                    test_date,
                ),
            )

            cursor.execute(
                """
                INSERT INTO newsletter_stats (date, posts_sent, total_score, avg_score)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date) 
                DO UPDATE SET 
                    posts_sent = EXCLUDED.posts_sent,
                    total_score = EXCLUDED.total_score,
                    avg_score = EXCLUDED.avg_score
            """,
                (test_date, 1, 100, 100.0),
            )

            print("✅ 测试数据插入成功")

            # 查询测试
            cursor.execute("SELECT COUNT(*) FROM sent_posts;")
            posts_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM newsletter_stats;")
            stats_count = cursor.fetchone()[0]

            print(f"✅ 数据查询成功 - sent_posts: {posts_count} 条，newsletter_stats: {stats_count} 条")

            # 清理测试数据
            cursor.execute("DELETE FROM sent_posts WHERE post_id = 'test_post_123';")
            cursor.execute("DELETE FROM newsletter_stats WHERE date = %s;", (test_date,))
            print("✅ 测试数据清理完成")

            cursor.close()
            self.connection.commit()
            return True

        except psycopg2.Error as e:
            print(f"❌ Newsletter 表测试失败: {e}")
            return False

    def test_config_validation(self):
        """测试配置验证"""
        print("🔍 测试配置验证...")

        try:
            # 验证配置完整性
            is_valid = self.config.validate_config()

            if is_valid:
                print("✅ 配置验证通过")

                # 显示配置摘要
                summary = self.config.get_config_summary()
                print("📋 配置摘要:")
                print(f"   数据库类型: {summary.get('database_type', 'N/A')}")
                print(f"   数据库主机: {summary.get('database_host', 'N/A')}")
                print(f"   数据库名称: {summary.get('database_name', 'N/A')}")

                return True
            else:
                print("❌ 配置验证失败")
                return False

        except Exception as e:
            print(f"❌ 配置验证出错: {e}")
            return False

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("📝 数据库连接已关闭")

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("PostgreSQL 数据库连接测试")
        print("=" * 60)

        tests = [
            ("配置验证", self.test_config_validation),
            ("基础连接", self.test_basic_connection),
            ("数据库版本", self.test_database_version),
            ("数据库权限", self.test_permissions),
            ("Newsletter 表结构", self.test_newsletter_tables_creation),
        ]

        results = []

        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}测试:")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name}测试出现异常: {e}")
                results.append((test_name, False))

        # 关闭连接
        self.close_connection()

        # 显示总结
        print("\n" + "=" * 60)
        print("测试结果总结:")
        print("=" * 60)

        passed = 0
        failed = 0

        for test_name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{test_name}: {status}")

            if success:
                passed += 1
            else:
                failed += 1

        print(f"\n总计: {passed} 个通过, {failed} 个失败")

        if failed == 0:
            print("\n🎉 所有 PostgreSQL 连接测试都通过了！")
            print("您的数据库配置正确，可以正常使用。")
        else:
            print(f"\n⚠️ 有 {failed} 个测试失败，请检查配置和连接。")

        return failed == 0


def main():
    """主函数"""
    try:
        test = PostgreSQLConnectionTest()
        return test.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
