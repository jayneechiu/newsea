"""
邮件发送功能测试模块
用于测试SMTP连接和邮件发送功能
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smtplib
import socket
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


class EmailConnectionTest:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")

    def test_basic_connection(self):
        """测试基础网络连接"""
        print("🔍 测试基础网络连接...")
        try:
            sock = socket.create_connection((self.smtp_server, self.smtp_port), timeout=30)
            print(f"✅ 成功连接到 {self.smtp_server}:{self.smtp_port}")
            sock.close()
            return True
        except Exception as e:
            print(f"❌ 网络连接失败: {e}")
            return False

    def test_smtp_connection(self):
        """测试SMTP连接和认证"""
        print("\n🔍 测试SMTP连接和认证...")
        print(f"服务器: {self.smtp_server}:{self.smtp_port}")
        print(f"用户名: {self.username}")
        print(f"密码: {'*' * len(self.password) if self.password else 'None'}")
        print("-" * 50)

        try:
            # 创建SMTP连接
            print("步骤 1: 创建SMTP连接...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            print("✅ SMTP连接创建成功")

            # 发送EHLO
            print("步骤 2: 发送EHLO命令...")
            server.ehlo()
            print("✅ EHLO命令成功")

            # 启动TLS
            print("步骤 3: 启动TLS加密...")
            server.starttls()
            print("✅ TLS启动成功")

            # TLS后重新EHLO
            print("步骤 4: TLS后重新发送EHLO...")
            server.ehlo()
            print("✅ TLS后EHLO成功")

            # 登录
            print("步骤 5: 尝试登录...")
            server.login(self.username, self.password)
            print("✅ 登录成功")

            server.quit()
            print("✅ 连接正常关闭")
            return True

        except socket.timeout:
            print("❌ 连接超时 - 可能是网络或防火墙问题")
            return False
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ 认证失败: {e}")
            print("\n💡 请检查:")
            print("   - Gmail账户是否启用了2FA")
            print("   - 是否使用了应用专用密码而不是账户密码")
            print("   - 应用密码是否正确（无空格）")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False

    def test_send_email(self):
        """测试发送测试邮件"""
        print("\n🔍 测试发送邮件...")

        if not self.recipients or not self.recipients[0].strip():
            print("❌ 没有配置收件人地址")
            return False

        try:
            # 创建SMTP连接
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.username, self.password)

            # 创建测试邮件
            msg = MIMEMultipart()
            msg["Subject"] = "Reddit Newsletter Bot - 邮件测试"
            msg["From"] = self.username
            msg["To"] = self.recipients[0].strip()

            body = """
这是一封测试邮件，用于验证Reddit Newsletter Bot的邮件发送功能。

如果您收到这封邮件，说明邮件配置完全正常！

测试时间: {}
""".format(
                os.popen("date /t && time /t").read().strip()
            )

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件
            server.send_message(msg)
            server.quit()

            print(f"✅ 测试邮件发送成功到: {self.recipients[0].strip()}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有邮件相关测试"""
        print("=" * 60)
        print("📧 邮件功能测试")
        print("=" * 60)

        # 检查配置
        if not all([self.username, self.password]):
            print("❌ 邮件配置不完整，请检查.env文件")
            return False

        results = []

        # 测试1: 基础网络连接
        results.append(self.test_basic_connection())

        # 测试2: SMTP连接和认证
        results.append(self.test_smtp_connection())

        # 测试3: 发送测试邮件
        results.append(self.test_send_email())

        # 结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        success_count = sum(results)
        total_tests = len(results)

        print(f"通过测试: {success_count}/{total_tests}")
        print(f"成功率: {success_count/total_tests*100:.1f}%")

        if success_count == total_tests:
            print("🎉 所有邮件测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查配置")

        return success_count == total_tests


def main():
    """主测试函数"""
    test = EmailConnectionTest()
    success = test.run_all_tests()
    return success


if __name__ == "__main__":
    main()
