"""Newsletter Sender - moved to app/backend/scraper"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Template
from typing import List, Dict
import os

logger = logging.getLogger(__name__)


class NewsletterSender:
    def __init__(self, config):
        self.config = config

    def send_newsletter(self, posts: List[Dict], editor_words: str = None) -> tuple[bool, str]:
        if editor_words is None:
            if self.config.get_enable_editor_summary():
                from .chatgpt_client import ChatGPTClient
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
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._generate_subject()
            msg["From"] = self.config.get_smtp_from_email()
            msg["To"] = ", ".join(self.config.get_recipients())
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            success = self._send_email(msg)
            if success:
                logger.info(f"Newsletter sent successfully with {len(posts)} posts")
            return success, editor_words
        except Exception as e:
            logger.error(f"Error sending newsletter: {e}")
            return False, editor_words

    def _generate_newsletter_html(self, posts: List[Dict], editor_words: str) -> str:
        template_path = os.path.join("templates", "newsletter_template2.html")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Newsletter template file does not exist: {template_path}")
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
        template_path = os.path.join("templates", "newsletter_template.txt")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            logger.warning(f"Text template file not found: {template_path}, using default format")
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
        lines = []
        lines.append(f"Reddit热门帖子 Newsletter - {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("=" * 50)
        lines.append(f"编辑寄语：{editor_words}\n")
        lines.append(f"今日精选：{len(posts)} 个热门帖子\n")
        for i, post in enumerate(posts, 1):
            lines.append(f"{i}. {post['title']}")
            lines.append(f"   版块: r/{post['subreddit']} | 作者: u/{post['author']}")
            lines.append(f"   评分: {post['score']} | 评论: {post['num_comments']}")
            if post.get("selftext"):
                lines.append(f"   内容: {post['selftext'][:100]}...")
            if post.get("gpt_summary"):
                lines.append(f"   分析: {post['gpt_summary']}")
            lines.append(f"   链接: {post['permalink']}")
            if post.get("url") and post["url"] != post["permalink"]:
                lines.append(f"   原始链接: {post['url']}")
            lines.append("")
        lines.append("此邮件由 Reddit Newsletter Bot 自动生成")
        return "\n".join(lines)

    def _generate_subject(self) -> str:
        return f"🔥 Reddit热门帖子 Newsletter - {datetime.now().strftime('%Y-%m-%d')}"

    def _send_email(self, msg: MIMEMultipart) -> bool:
        try:
            if self.config.get_smtp_use_ssl():
                server = smtplib.SMTP_SSL(self.config.get_smtp_server(), self.config.get_smtp_port())
            else:
                server = smtplib.SMTP(self.config.get_smtp_server(), self.config.get_smtp_port())
            if self.config.get_smtp_use_tls() and not self.config.get_smtp_use_ssl():
                server.starttls()
            if self.config.get_smtp_username() and self.config.get_smtp_password():
                server.login(self.config.get_smtp_username(), self.config.get_smtp_password())
            recipients = self.config.get_recipients()
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
        except smtplib.SMTPException as e:
            logger.error(f"SMTP send failed: {e}")
            return False

    def test_email_connection(self) -> bool:
        try:
            msg = MIMEMultipart()
            msg["Subject"] = "Reddit Newsletter Bot - 连接测试"
            msg["From"] = self.config.get_smtp_from_email()
            msg["To"] = ", ".join(self.config.get_recipients())
            part = MIMEText("这是一封测试邮件，用于验证SMTP连接配置是否正确。", "plain", "utf-8")
            msg.attach(part)
            success = self._send_email(msg)
            if success:
                logger.info("测试邮件发送成功！")
            else:
                logger.error("测试邮件发送失败！")
            return success
        except Exception as e:
            logger.error(f"测试邮件连接时出错: {e}")
            return False
