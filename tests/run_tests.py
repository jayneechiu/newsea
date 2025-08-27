"""
测试运行脚本
提供便捷的测试命令接口
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_usage():
    """打印使用说明"""
    print("Reddit Newsletter Bot - 测试工具")
    print("=" * 50)
    print("使用方法: python run_tests.py [选项]")
    print("\n可用选项:")
    print("  reddit      - 测试Reddit API连接")
    print("  email       - 测试邮件发送功能")
    print("  database    - 测试数据库功能")
    print("  full        - 运行完整系统测试")
    print("  all         - 同 'full'")
    print("  help        - 显示此帮助信息")
    print("\n示例:")
    print("  python run_tests.py reddit")
    print("  python run_tests.py email")
    print("  python run_tests.py full")

def run_reddit_test():
    """运行Reddit测试"""
    from test_reddit_connection import main
    return main()

def run_email_test():
    """运行邮件测试"""
    from test_email_connection import main
    return main()

def run_database_test():
    """运行数据库测试"""
    from test_database import main
    return main()

def run_full_test():
    """运行完整测试"""
    from test_full_system import main
    return main()

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print_usage()
        return False
    
    test_type = sys.argv[1].lower()
    
    try:
        if test_type == "reddit":
            return run_reddit_test()
        elif test_type == "email":
            return run_email_test()
        elif test_type == "database":
            return run_database_test()
        elif test_type in ["full", "all"]:
            return run_full_test()
        elif test_type == "help":
            print_usage()
            return True
        else:
            print(f"❌ 未知的测试类型: {test_type}")
            print_usage()
            return False
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
