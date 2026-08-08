import os
import requests
from typing import List
from .config_manager import ConfigManager


class ChatGPTClient:
    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()
        self.api_key = self.config.get_chatgpt_api_key()
        self.api_url = self.config.get_openai_api_base().rstrip("/") + "/chat/completions"
        self.model = self.config.get_openai_model()

    def summarize_and_analyze(self, post_title: str, post_content: str) -> str:
        prompt = f"""请为以下Reddit热门帖子生成一个简洁的中文总结。

标题：{post_title}
内容：{post_content}

要求：
1. 使用纯文本格式，不要使用Markdown符号（如**、#等）
2. 总结控制在30-40字以内
3. 一句话说明为什么受欢迎
4. 语言简洁流畅
5. 直接输出内容，不要添加标题

请开始："""
        response = self._call_gpt(prompt, max_tokens=80)
        response = response.replace("**", "").replace("#", "").replace("*", "")
        return response

    def generate_editor_words(self, posts: List[dict]) -> str:
        topics = []
        for i, post in enumerate(posts[:5], 1):
            topics.append(f"{i}. {post['title'][:100]}")
        topics_text = "\n".join(topics)
        prompt = f"""You are the editor of Newsea, a sharp visual digest of useful Reddit conversations.
Today's selected posts:

{topics_text}

Write one 35-55 word English opening paragraph.
Requirements:
1. Hint at the range of topics without listing or numbering every post.
2. Use light dry humor and a confident editorial voice.
3. Create curiosity; do not reveal every conclusion.
4. Do not invent facts or add background absent from the titles.
5. No Markdown, emoji, heading, or quotation marks.
6. Return only the paragraph."""
        response = self._call_gpt(prompt, max_tokens=120)
        return response

    def summarize_comments(self, comments: List[dict]) -> str:
        if not comments:
            return "暂无精彩评论"
        comments_text = "\n\n".join([f"用户 {c['author']} ({c['score']}赞):\n{c['body'][:200]}" for c in comments[:5]])
        prompt = f"""请总结以下Reddit帖子评论区的精华观点。

评论内容：
{comments_text}

要求：
1. 用中文总结
2. 提炼2-3个最有价值的观点或讨论
3. 每个观点一句话，总字数控制在60字以内
4. 保持客观中立
5. 直接输出观点，不要添加标题或前缀

请开始："""
        response = self._call_gpt(prompt, max_tokens=120)
        return response

    def generate_newsletter_teaser(
        self, post_title: str, summary: str = "", comment_summary: str = ""
    ) -> str:
        """Create a short, accurate hook for the email without giving everything away."""
        prompt = f"""Write one English teaser sentence for a Newsea email.

Reddit post title: {post_title}
Summary: {summary}
Community discussion: {comment_summary}

Requirements:
1. 16-28 words.
2. Create curiosity without hiding the basic topic.
3. Use light dry humor when it fits; never force a joke.
4. Do not list takeaways or reveal the full conclusion.
5. Do not invent facts, numbers, quotes, or identities.
6. No Markdown, emoji, label, or quotation marks.
7. Return only the sentence.
"""
        teaser = self._call_gpt(prompt, max_tokens=60)
        if teaser.startswith("[") and "失败" in teaser:
            return summary or post_title
        return teaser

    def _call_gpt(self, prompt: str, max_tokens: int = 300) -> str:
        if not self.api_key:
            return "[ChatGPT分析失败: API密钥未配置]"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
        try:
            resp = requests.post(self.api_url, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            return f"[ChatGPT分析失败: 请求超时]"
        except requests.exceptions.ConnectionError:
            return f"[ChatGPT分析失败: 网络连接错误]"
        except requests.exceptions.HTTPError as e:
            return f"[ChatGPT分析失败: HTTP错误 {e.response.status_code}]"
        except KeyError:
            return f"[ChatGPT分析失败: 响应格式异常]"
        except Exception as e:
            return f"[ChatGPT分析失败: {str(e)[:50]}]"
