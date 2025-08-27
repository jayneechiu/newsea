"""
完整系统测试模块
运行所有测试并生成综合报告
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from test_reddit_connection import RedditConnectionTest
from test_email_connection import EmailConnectionTest
from test_database import DatabaseTest

class FullSystemTest:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
    
    def run_all_tests(self):
        """运行所有系统测试"""
        print("🚀 Reddit Newsletter Bot - 完整系统测试")
        print("=" * 80)
        print(f"测试开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. Reddit连接测试
        print("\n1️⃣ Reddit API连接测试")
        print("-" * 40)
        reddit_test = RedditConnectionTest()
        self.test_results['reddit'] = reddit_test.test_connection()
        
        # 2. 邮件功能测试
        print("\n2️⃣ 邮件发送功能测试")
        print("-" * 40)
        email_test = EmailConnectionTest()
        self.test_results['email'] = email_test.run_all_tests()
        
        # 3. 数据库功能测试
        print("\n3️⃣ 数据库功能测试")
        print("-" * 40)
        db_test = DatabaseTest()
        self.test_results['database'] = db_test.run_all_tests()
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("📊 完整测试报告")
        print("=" * 80)
        
        # 测试结果汇总
        print("测试模块结果:")
        print(f"  Reddit API连接: {'✅ 通过' if self.test_results.get('reddit') else '❌ 失败'}")
        print(f"  邮件发送功能: {'✅ 通过' if self.test_results.get('email') else '❌ 失败'}")
        print(f"  数据库功能: {'✅ 通过' if self.test_results.get('database') else '❌ 失败'}")
        
        # 总体结果
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        success_rate = passed_tests / total_tests * 100
        
        print(f"\n总体结果:")
        print(f"  通过测试: {passed_tests}/{total_tests}")
        print(f"  成功率: {success_rate:.1f}%")
        print(f"  测试耗时: {duration.total_seconds():.2f}秒")
        
        # 系统状态判断
        if passed_tests == total_tests:
            print("\n🎉 系统状态: 完全正常")
            print("✅ Reddit Newsletter Bot 已准备就绪，可以正常运行！")
        elif passed_tests >= total_tests * 0.67:  # 67%以上通过
            print("\n⚠️ 系统状态: 基本正常")
            print("💡 建议修复失败的模块以获得最佳性能")
        else:
            print("\n❌ 系统状态: 需要修复")
            print("🔧 请修复失败的模块后再运行主程序")
        
        # 建议
        if not self.test_results.get('reddit'):
            print("\n🔧 Reddit API修复建议:")
            print("   - 检查.env文件中的Reddit API凭据")
            print("   - 确认网络连接正常")
            print("   - 验证Reddit应用权限设置")
        
        if not self.test_results.get('email'):
            print("\n🔧 邮件功能修复建议:")
            print("   - 检查Gmail账户2FA设置")
            print("   - 确认应用专用密码正确")
            print("   - 检查网络防火墙设置")
        
        if not self.test_results.get('database'):
            print("\n🔧 数据库修复建议:")
            print("   - 检查数据库文件权限")
            print("   - 确认SQLite安装正确")
            print("   - 验证磁盘空间充足")
        
        print("\n" + "=" * 80)
        print(f"测试完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return passed_tests == total_tests

def main():
    """主测试函数"""
    test_suite = FullSystemTest()
    success = test_suite.run_all_tests()
    
    # 返回退出代码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
