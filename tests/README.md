# Reddit Newsletter Bot - 测试模块

本目录包含 Reddit Newsletter Bot 的所有测试文件，用于验证系统各个组件的功能。

## 📁 文件结构

```
tests/
├── __init__.py                      # 测试模块初始化
├── README.md                        # 测试说明文档
├── run_tests.py                     # 测试运行脚本
├── test_reddit_connection.py        # Reddit API连接测试
├── test_email_connection.py         # 邮件发送功能测试
├── test_postgres_connection.py      # PostgreSQL 数据库连接测试
├── test_gpt_connection.py           # GPT API连接测试
└── test_full_system.py             # 完整系统测试
```

## 🚀 快速开始

### 运行所有测试

```bash
cd tests
python run_tests.py all
```

### 运行单个测试模块

```bash
# 测试Reddit API连接
python run_tests.py reddit

# 测试邮件发送功能
python run_tests.py email

# 测试 PostgreSQL 数据库连接
python run_tests.py database
```

### 直接运行测试文件

```bash
# Reddit连接测试
python test_reddit_connection.py

# 邮件连接测试
python test_email_connection.py

# PostgreSQL 数据库测试
python test_postgres_connection.py

# GPT连接测试
python test_gpt_connection.py

# 完整系统测试
python test_full_system.py
```

## 📋 测试模块说明

### 1. Reddit API 连接测试 (`test_reddit_connection.py`)

- ✅ 验证 Reddit API 凭据
- ✅ 测试用户认证
- ✅ 获取热门帖子样本

### 2. 邮件发送功能测试 (`test_email_connection.py`)

- ✅ 基础网络连接测试
- ✅ SMTP 服务器连接和认证
- ✅ TLS 加密连接
- ✅ 实际邮件发送测试

### 3. PostgreSQL 数据库测试 (`test_postgres_connection.py`)

- ✅ PostgreSQL 数据库连接验证
- ✅ 配置验证和连接信息检查
- ✅ 数据库版本和权限测试
- ✅ Newsletter 表结构创建测试
- ✅ 数据插入、查询、更新操作测试

### 4. GPT API 连接测试 (`test_gpt_connection.py`)

- ✅ OpenAI API key 验证
- ✅ GPT 模型连接测试
- ✅ 基础对话功能测试
- ✅ Reddit 帖子总结功能测试
- ✅ Token 使用统计

### 5. 完整系统测试 (`test_full_system.py`)

- ✅ 运行所有上述测试
- ✅ 生成综合测试报告
- ✅ 提供系统状态评估
- ✅ 给出修复建议

## 🔧 故障排除

### Reddit API 测试失败

```
💡 检查项目：
- .env 文件中的 Reddit API 凭据是否正确
- 网络连接是否正常
- Reddit 应用权限设置是否正确
```

### 邮件测试失败

```
💡 检查项目：
- Gmail 账户是否启用 2FA
- 应用专用密码是否正确配置
- 网络防火墙是否阻止 SMTP 连接
```

### PostgreSQL 数据库测试失败

- 检查 `DATABASE_URL` 配置是否正确
- 确认 PostgreSQL 数据库服务运行正常
- 验证数据库用户权限和网络连接

```
💡 检查项目：
- Azure PostgreSQL 或 Supabase 数据库服务状态
- 数据库连接字符串格式
- 网络连接和防火墙设置
```

## 📊 测试输出说明

测试输出使用以下符号：

- ✅ 测试通过
- ❌ 测试失败
- ⚠️ 警告信息
- 💡 建议或提示
- 🔍 正在执行的操作
- 📊 统计信息
- 🎉 全部成功

## 🛠️ 开发说明

### 添加新测试

1. 在对应的测试文件中添加新的测试方法
2. 更新 `run_all_tests()` 方法包含新测试
3. 更新测试文档

### 测试规范

- 所有测试方法返回 `True`（成功）或 `False`（失败）
- 使用统一的输出格式（✅/❌）
- 提供详细的错误信息和修复建议
- 包含必要的清理操作

## 📝 配置要求

确保 `.env` 文件包含以下配置：

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
REDDIT_USER_AGENT=your_user_agent

# PostgreSQL 数据库
DATABASE_URL=postgresql://username:password@host:port/database

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# OpenAI (可选)
OPENAI_API_KEY=your_openai_api_key
```

运行测试前请确保所有必要的配置都已正确设置。
