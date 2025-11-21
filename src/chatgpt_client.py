import os
import requests
from typing import List
from .config_manager import ConfigManager


class ChatGPTClient:
    def __init__(self, config_manager: ConfigManager = None):
        """
        初始化 ChatGPT 客户端

        Args:
            config_manager: 配置管理器实例，如果为None则创建新实例
        """
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
        # 清理可能的Markdown符号
        response = response.replace("**", "").replace("#", "").replace("*", "")
        return response

    def generate_editor_words(self, posts: List[dict]) -> str:
        # 提取帖子标题（按热度排序）
        topics = []
        for i, post in enumerate(posts[:5], 1):  # 取前5个帖子
            topics.append(f"{i}. {post['title'][:100]}")
        
        topics_text = "\n".join(topics)
        
        prompt = f"""你是一个风趣幽默的Reddit Newsletter编辑。今天的热门帖子（按热度排序）：

{topics_text}

请写一段60-80字的开场白，像一条推文的风格，要求：
1. 必须提及所有5个帖子，按1-5的顺序串联
2. 冷幽默风格，用调侃、吐槽或反转的手法串联这些话题
3. 适度补充新闻背景，解释帖子为什么热门
4. 语言简洁有力，像在发推文/微博
5. 不要用序号，要自然地串联所有话题
6. 直接输出内容，不要加引号或标题

现在请开始："""
        
        response = self._call_gpt(prompt, max_tokens=180)
        return response

    def summarize_comments(self, comments: List[dict]) -> str:
        """
        总结评论区的精华观点

        Args:
            comments: 评论列表，每个评论包含 author, body, score 等字段

        Returns:
            评论区精华总结
        """
        if not comments:
            return "暂无精彩评论"

        # 构建评论文本
        comments_text = "\n\n".join(
            [f"用户 {c['author']} ({c['score']}赞):\n{c['body'][:200]}" for c in comments[:5]]
        )

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

    def _call_gpt(self, prompt: str, max_tokens: int = 300) -> str:
        """调用 GPT API"""
        if not self.api_key:
            return "[ChatGPT分析失败: API密钥未配置]"

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
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
