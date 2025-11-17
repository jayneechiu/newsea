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
        prompt = """作为Reddit Newsletter的编辑，请为本期内容写一段简短的编辑寄语。

要求：
1. 用中文写作，语调亲切自然
2. 突出本期亮点
3. 30-50字左右
4. 不要包含署名、祝好等结尾格式
5. 直接输出寄语内容

请开始："""
        response = self._call_gpt(prompt, max_tokens=100)
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
