import requests
import base64
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ======= Reddit 配置 (从环境变量读取) =======
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDDIT_REDIRECT_URI', 'http://localhost:8080')
AUTHORIZATION_CODE = input('请输入授权码: ')  # 用户输入，不在代码中硬编码
USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Reddit Newsletter Bot v1.0')
# ==========================================

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ 错误: 请在.env文件中设置REDDIT_CLIENT_ID和REDDIT_CLIENT_SECRET")
    exit(1)

if not AUTHORIZATION_CODE:
    print("❌ 错误: 授权码不能为空")
    exit(1)

# Base64 编码
basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

headers = {
    'Authorization': f'Basic {basic_auth}',
    'User-Agent': USER_AGENT,
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'authorization_code',
    'code': AUTHORIZATION_CODE,
    'redirect_uri': REDIRECT_URI
}

response = requests.post(
    'https://www.reddit.com/api/v1/access_token',
    headers=headers,
    data=data
)

if response.status_code == 200:
    tokens = response.json()
    print("✅ 成功获取 Refresh Token：")
    print("Refresh Token:", tokens.get("refresh_token"))
    print("Access Token:", tokens.get("access_token"))
else:
    print("❌ 获取失败！状态码:", response.status_code)
    print(response.text)
