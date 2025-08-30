#!/usr/bin/env python3
"""
GPT 连接测试脚本
测试 OpenAI GPT API 连接和功能
"""
import logging
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager import ConfigManager
from openai import OpenAI

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_gpt_connection():
    """测试 GPT API 连接"""
    try:
        # 加载配置 - 确保使用正确的配置文件路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(project_root, '.env')
        config = ConfigManager(config_file)
        
        # 检查 API key
        api_key = config.get_openai_api_key()
        if not api_key:
            logger.error("❌ OpenAI API key 未设置")
            return False
        
        logger.info(f"✅ OpenAI API key 已设置 (长度: {len(api_key)})")
        logger.info(f"✅ API Base: {config.get_openai_api_base()}")
        logger.info(f"✅ 模型: {config.get_openai_model()}")
        
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url=config.get_openai_api_base()
        )
        
        logger.info("🔄 正在测试 API 连接...")
        
        # 发送简单的测试请求
        response = client.chat.completions.create(
            model=config.get_openai_model(),
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请简单回复：连接成功"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        # 获取响应
        if response.choices and response.choices[0].message:
            reply = response.choices[0].message.content.strip()
            logger.info(f"✅ GPT API 连接成功！")
            logger.info(f"📝 GPT 回复: {reply}")
            
            # 显示使用的 tokens
            usage = response.usage
            if usage:
                logger.info(f"📊 Token 使用: 输入 {usage.prompt_tokens}, 输出 {usage.completion_tokens}, 总计 {usage.total_tokens}")
            
            return True
        else:
            logger.error("❌ GPT API 响应格式异常")
            return False
            
    except Exception as e:
        logger.error(f"❌ GPT API 连接失败: {e}")
        return False

def test_reddit_summary():
    """测试 Reddit 帖子总结功能"""
    try:
        # 加载配置 - 确保使用正确的配置文件路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(project_root, '.env')
        config = ConfigManager(config_file)
        
        # 模拟一个 Reddit 帖子
        test_post = {
            'title': 'TIL that in 2008 Hugh Laurie made a single, off-hand comment claiming that a perk of being a celebrity was having a special lifetime, unlimited Burger King Crown Card',
            'content': 'He actually didn\'t have one, but after his comment caused a huge public response, BK gave him one.',
            'url': 'https://reddit.com/r/todayilearned/example',
            'subreddit': 'todayilearned',
            'score': 15420,
            'comments': 892
        }
        
        logger.info("🔄 测试 Reddit 帖子总结功能...")
        
        client = OpenAI(
            api_key=config.get_openai_api_key(),
            base_url=config.get_openai_api_base()
        )
        
        # 创建总结请求
        prompt = f"""请为以下 Reddit 帖子生成一个简洁的中文总结（50字以内）：

标题: {test_post['title']}
内容: {test_post['content']}
来源: r/{test_post['subreddit']}

要求：
1. 使用简洁的中文
2. 突出主要信息
3. 保持客观中性
4. 不超过50字"""

        response = client.chat.completions.create(
            model=config.get_openai_model(),
            messages=[
                {"role": "system", "content": "你是一个专业的新闻总结助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        if response.choices and response.choices[0].message:
            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ Reddit 帖子总结测试成功！")
            logger.info(f"📝 原标题: {test_post['title'][:80]}...")
            logger.info(f"📝 GPT 总结: {summary}")
            return True
        else:
            logger.error("❌ Reddit 帖子总结测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ Reddit 帖子总结测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== GPT API 连接测试 ===\n")
    
    # 基础连接测试
    basic_test = test_gpt_connection()
    
    print("\n" + "="*50 + "\n")
    
    # Reddit 总结功能测试
    if basic_test:
        summary_test = test_reddit_summary()
    else:
        logger.warning("⚠️ 基础连接测试失败，跳过总结功能测试")
        summary_test = False
    
    print("\n" + "="*50 + "\n")
    
    # 最终结果
    if basic_test and summary_test:
        logger.info("🎉 所有 GPT 功能测试通过！")
        sys.exit(0)
    elif basic_test:
        logger.warning("⚠️ 基础连接正常，但总结功能有问题")
        sys.exit(1)
    else:
        logger.error("❌ GPT API 连接失败")
        sys.exit(1)
