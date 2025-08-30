#!/usr/bin/env python3
"""
测试修改后的 ChatGPTClient 类
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager import ConfigManager
from src.chatgpt_client import ChatGPTClient

def test_chatgpt_client():
    """测试 ChatGPTClient 类"""
    print("=== 测试 ChatGPTClient 类 ===\n")
    
    # 加载配置
    config = ConfigManager()
    
    # 检查配置
    print(f"✅ OpenAI API Key: {'已设置' if config.get_openai_api_key() else '未设置'}")
    print(f"✅ API Base: {config.get_openai_api_base()}")
    print(f"✅ 模型: {config.get_openai_model()}")
    print()
    
    # 初始化客户端
    try:
        client = ChatGPTClient(config)
        print("✅ ChatGPTClient 初始化成功")
        print(f"   - 使用模型: {client.model}")
        print(f"   - API URL: {client.api_url}")
        print()
    except Exception as e:
        print(f"❌ ChatGPTClient 初始化失败: {e}")
        return False
    
    # 测试总结功能
    print("🔄 测试帖子总结功能...")
    try:
        test_title = "TIL that in 2008 Hugh Laurie made a comment about having unlimited Burger King"
        test_content = "He didn't actually have one, but BK gave him one after his comment went viral."
        
        summary = client.summarize_and_analyze(test_title, test_content)
        print("✅ 帖子总结测试成功！")
        print(f"📝 总结结果: {summary}")
        print()
    except Exception as e:
        print(f"❌ 帖子总结测试失败: {e}")
        return False
    
    # 测试编辑寄语功能
    print("🔄 测试编辑寄语功能...")
    try:
        test_posts = [
            {"title": "Amazing discovery", "score": 1000},
            {"title": "Interesting fact", "score": 500}
        ]
        
        editor_words = client.generate_editor_words(test_posts)
        print("✅ 编辑寄语测试成功！")
        print(f"📝 编辑寄语: {editor_words}")
        print()
    except Exception as e:
        print(f"❌ 编辑寄语测试失败: {e}")
        return False
    
    print("🎉 所有 ChatGPTClient 测试通过！")
    return True

if __name__ == "__main__":
    success = test_chatgpt_client()
    if success:
        print("\n✅ ChatGPTClient 类修改成功，功能正常！")
        sys.exit(0)
    else:
        print("\n❌ ChatGPTClient 类存在问题！")
        sys.exit(1)
