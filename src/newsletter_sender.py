"""
Newsletter Sender - 邮件发送模块
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from jinja2 import Template
from typing import List, Dict
import os

logger = logging.getLogger(__name__)


class NewsletterSender:
    """Newsletter邮件发送器"""

    def __init__(self, config):
        self.config = config

    def send_newsletter(self, posts: List[Dict], editor_words: str = None) -> tuple[bool, str]:
        """发送Newsletter邮件

        Args:
            posts: 帖子列表
            editor_words: 编辑寄语（可选）。如果不提供，将根据配置自动生成
        """
        if editor_words is None:
            if self.config.get_enable_editor_summary():
                from src.chatgpt_client import ChatGPTClient

                gpt_client = ChatGPTClient(self.config)
                try:
                    editor_words = gpt_client.generate_editor_words(posts)
                except Exception as e:
                    editor_words = f"[编辑寄语生成失败: {e}]"
            else:
                editor_words = "欢迎阅读本期 Reddit 热门帖子精选！"

        try:
            html_content = self._generate_newsletter_html(posts, editor_words)
            text_content = self._generate_newsletter_text(posts, editor_words)

            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._generate_subject()
            msg["From"] = self.config.get_smtp_from_email()
            msg["To"] = ", ".join(self.config.get_recipients())

            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")

            msg.attach(part1)
            msg.attach(part2)

            success = self._send_email(msg)

            if success:
                logger.info(f"Newsletter发送成功，包含 {len(posts)} 个帖子")

            return success, editor_words

        except Exception as e:
            logger.error(f"发送Newsletter时出错: {e}")
            return False, editor_words

    def _generate_newsletter_html(self, posts: List[Dict], editor_words: str) -> str:
        """生成HTML格式的Newsletter内容"""
        template_path = os.path.join("templates", "newsletter_template2.html")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            logger.error(f"模板文件未找到: {template_path}")
            raise FileNotFoundError(f"Newsletter模板文件不存在: {template_path}")
        template = Template(template_content)
        return template.render(
            posts=posts,
            top_post=posts[0] if posts else None,
            date=datetime.now().strftime("%Y-%m-%d"),
            total_posts=len(posts),
            editor_words=editor_words,
            editor_name=self.config.get_newsletter_editor_name(),
            newsletter_title=self.config.get_newsletter_title(),
        )

    def _generate_newsletter_text(self, posts: List[Dict], editor_words: str) -> str:
        """生成纯文本格式的Newsletter内容"""
        template_path = os.path.join("templates", "newsletter_template.txt")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            logger.warning(f"文本模板文件未找到: {template_path}，使用默认格式")
            return self._generate_default_text(posts, editor_words)
        template = Template(template_content)
        return template.render(
            posts=posts,
            date=datetime.now().strftime("%Y-%m-%d"),
            total_posts=len(posts),
            editor_words=editor_words,
            editor_name=self.config.get_newsletter_editor_name(),
            newsletter_title=self.config.get_newsletter_title(),
        )

    def _generate_default_text(self, posts: List[Dict], editor_words: str) -> str:
        """生成默认的纯文本Newsletter内容"""
        lines = []
        lines.append(f"Reddit热门帖子 Newsletter - {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("=" * 50)
        lines.append(f"编辑寄语：{editor_words}\n")
        lines.append(f"今日精选：{len(posts)} 个热门帖子\n")
        for i, post in enumerate(posts, 1):
            lines.append(f"{i}. {post['title']}")
            lines.append(f"   版块: r/{post['subreddit']} | 作者: u/{post['author']}")
            lines.append(f"   评分: {post['score']} | 评论: {post['num_comments']}")
            if post["selftext"]:
                lines.append(f"   内容: {post['selftext'][:100]}...")
            if post.get("gpt_summary"):
                lines.append(f"   分析: {post['gpt_summary']}")
            lines.append(f"   链接: {post['permalink']}")
            if post["url"] != post["permalink"]:
                lines.append(f"   原始链接: {post['url']}")
            lines.append("")
        lines.append("此邮件由 Reddit Newsletter Bot 自动生成")
        return "\n".join(lines)

    def _generate_subject(self) -> str:
        """生成邮件主题"""
        return f"🔥 Reddit热门帖子 Newsletter - {datetime.now().strftime('%Y-%m-%d')}"

    def _send_email(self, msg: MIMEMultipart) -> bool:
        """发送邮件"""
        try:
            # 创建SMTP连接
            if self.config.get_smtp_use_ssl():
                server = smtplib.SMTP_SSL(self.config.get_smtp_server(), self.config.get_smtp_port())
            else:
                server = smtplib.SMTP(self.config.get_smtp_server(), self.config.get_smtp_port())

            if self.config.get_smtp_use_tls() and not self.config.get_smtp_use_ssl():
                server.starttls()

            # 登录
            if self.config.get_smtp_username() and self.config.get_smtp_password():
                server.login(self.config.get_smtp_username(), self.config.get_smtp_password())

            # 发送邮件
            recipients = self.config.get_recipients()
            server.send_message(msg, to_addrs=recipients)
            server.quit()

            logger.info(f"邮件发送成功到 {len(recipients)} 个收件人")
            return True

        except Exception as e:
            logger.error(f"SMTP发送失败: {e}")
            return False

    def test_email_connection(self) -> bool:
        """测试邮件连接"""
        try:
            # 创建测试邮件
            msg = MIMEMultipart()
            msg["Subject"] = "Reddit Newsletter Bot - 连接测试"
            msg["From"] = self.config.get_smtp_from_email()
            msg["To"] = ", ".join(self.config.get_recipients())

            # 添加测试内容
            test_content = "这是一封测试邮件，用于验证SMTP连接配置是否正确。"
            part = MIMEText(test_content, "plain", "utf-8")
            msg.attach(part)

            # 发送测试邮件
            success = self._send_email(msg)

            if success:
                logger.info("测试邮件发送成功！")
            else:
                logger.error("测试邮件发送失败！")

            return success

        except Exception as e:
            logger.error(f"测试邮件连接时出错: {e}")
            return False
