# Reddit Newsletter Bot 🚀

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Reddit API](https://img.shields.io/badge/Reddit-API-orange.svg)](https://www.reddit.com/dev/api/)

一个智能的 Reddit 热门帖子聚合器，自动生成精美的 Newsletter 并定时发送。集成 OpenAI GPT 进行内容总结和分析。

## ✨ 主要功能

- 🔥 **多版块热门抓取** - 支持自定义 Subreddit 和抓取规则
- 🤖 **AI 智能总结** - GPT 驱动的帖子总结和受欢迎度分析
- 📧 **精美邮件模板** - 响应式 HTML 设计，支持纯文本版本
- ⏰ **定时自动发送** - 可配置的发送时间和频率
- 💾 **完整历史记录** - 保存所有发送记录和 AI 生成内容
- 📊 **统计与管理** - 发送成功率、内容统计等
- 🛠️ **丰富的工具** - 测试、管理、清理等实用工具

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/jayneechiu/newsea.git
cd newsea
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 配置

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的 API 密钥和设置。

### 3. 运行

```bash
# 验证配置
python tools/manage.py validate-config

# 测试所有功能
python tools/manage.py test-all

# 立即发送 Newsletter
python tools/manage.py send-now

# 启动定时服务
python main.py
```

## ⚙️ 配置说明

### Reddit API 配置

1. 访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. 创建新应用（选择 "script" 类型）
3. 在 `.env` 中配置相关参数

### OpenAI API 配置

1. 获取 [OpenAI API Key](https://platform.openai.com/api-keys)
2. 在 `.env` 中设置 `OPENAI_API_KEY`
3. 可选择不同的 GPT 模型（推荐 `gpt-4o-mini`）

### 邮件服务配置

支持任何 SMTP 邮件服务：

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

## 🛠️ 管理工具

```bash
# 测试命令
python tools/manage.py test-reddit     # 测试 Reddit API
python tools/manage.py test-email      # 测试邮件发送
python tools/manage.py test-all        # 完整系统测试

# 运行命令
python tools/manage.py send-now        # 立即发送
python tools/manage.py stats           # 显示统计信息
python tools/manage.py history         # 查看发送历史

# 维护命令
python tools/manage.py cleanup --days 30  # 清理旧数据
python tools/manage.py validate-config    # 验证配置
```

## 📁 项目结构

```
├── src/                    # 核心源代码
│   ├── reddit_scraper.py   # Reddit API 集成
│   ├── chatgpt_client.py   # OpenAI GPT 集成
│   ├── newsletter_sender.py # 邮件发送模块
│   ├── database_manager.py # 数据库管理
│   └── config_manager.py   # 配置管理
├── templates/              # 邮件模板
├── tools/                  # 管理工具
├── tests/                  # 测试模块
├── data/                   # 数据文件
└── main.py                # 主程序入口
```

## 📊 功能亮点

### AI 智能总结

- 使用 GPT 对每个热门帖子进行总结和分析
- 生成个性化的编辑寄语
- 智能识别帖子受欢迎的原因

### 完整历史记录

- 保存所有发送的 Newsletter 内容
- 记录 AI 生成的总结和寄语
- 支持历史内容查询和分析

### 灵活配置

- 支持多个 Subreddit 同时抓取
- 可配置的帖子数量和过滤条件
- 灵活的发送时间和频率设置

## 🔧 开发

### 环境要求

- Python 3.11+
- SQLite 3
- 网络连接（用于 API 调用）

### 测试

```bash
cd tests/
python test_reddit_connection.py
python test_gpt_connection.py
python test_full_system.py
```

### 贡献

欢迎提交 Issue 和 Pull Request！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解更多信息。

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新内容。

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PRAW](https://github.com/praw-dev/praw) - Reddit API 客户端
- [OpenAI](https://openai.com/) - GPT API 服务
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎

1. 启用 2FA（两步验证）
2. 生成应用专用密码
3. 使用应用密码而不是账户密码

### 6. 设置配置文件

复制并编辑配置文件：

```bash
copy .env.example .env
```

编辑`.env`文件，填入你的配置信息：

```env
# Reddit API 配置
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# 邮件配置
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# 目标Subreddit（可自定义）
TARGET_SUBREDDITS=AskReddit,todayilearned,worldnews,technology,science
```

### 7. 测试配置

使用管理工具验证所有功能：

```bash
# 验证配置文件
python tools/manage.py validate-config

# 测试 Reddit API 连接
python tools/manage.py test-reddit

# 测试邮件发送功能
python tools/manage.py test-email

# 运行完整系统测试
python tools/manage.py test-all
```

**或者使用独立的测试系统：**

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定测试
python tests/test_reddit_connection.py
python tests/test_email_connection.py
python tests/test_database.py
python tests/test_full_system.py
```

### 8. 启动服务

```bash
python main.py
```

## 配置说明

### Reddit 配置

| 配置项                   | 说明                 | 示例                  |
| ------------------------ | -------------------- | --------------------- |
| `REDDIT_CLIENT_ID`       | Reddit 应用 ID       | `abc123def456`        |
| `REDDIT_CLIENT_SECRET`   | Reddit 应用密钥      | `xyz789abc123`        |
| `REDDIT_USERNAME`        | Reddit 用户名        | `your_username`       |
| `REDDIT_PASSWORD`        | Reddit 密码          | `your_password`       |
| `TARGET_SUBREDDITS`      | 目标版块（逗号分隔） | `AskReddit,worldnews` |
| `POSTS_LIMIT`            | 每个版块抓取数量     | `25`                  |
| `NEWSLETTER_POSTS_LIMIT` | Newsletter 包含数量  | `10`                  |

### 邮件配置

| 配置项             | 说明               | 示例                |
| ------------------ | ------------------ | ------------------- |
| `SMTP_SERVER`      | SMTP 服务器        | `smtp.gmail.com`    |
| `SMTP_PORT`        | SMTP 端口          | `587`               |
| `SMTP_USERNAME`    | 邮箱用户名         | `user@gmail.com`    |
| `SMTP_PASSWORD`    | 邮箱密码/应用密码  | `app_password`      |
| `EMAIL_RECIPIENTS` | 收件人（逗号分隔） | `user1@example.com` |

### 定时配置

| 配置项            | 说明           | 示例    |
| ----------------- | -------------- | ------- |
| `SCHEDULE_TIME`   | 每日发送时间   | `09:00` |
| `RUN_IMMEDIATELY` | 启动时立即运行 | `false` |

## 工具脚本使用

项目提供了`tools.py`脚本来进行各种管理操作：

```bash
# 验证配置
python tools.py validate-config

# 测试Reddit连接
python tools.py test-reddit

# 测试邮件发送
python tools.py test-email

# 运行完整测试
python tools.py test-all

# 立即发送一次Newsletter
python tools.py send-now

# 查看统计信息
python tools.py stats

# 清理旧数据（默认90天前）
python tools.py cleanup --days 90
```

## Newsletter 预览

Newsletter 邮件包含以下内容：

- 📅 发送日期
- 📊 帖子总数统计
- 🔥 热门帖子列表：
  - 帖子标题（链接到 Reddit）
  - 版块和作者信息
  - 评分和评论数
  - 帖子摘要（如果有）
  - 原始链接（如果不同于 Reddit 链接）

## 项目结构

```
reddit-newsletter-bot/
├── main.py                 # 主程序入口
├── test.py                 # 快速测试脚本
├── tools.py                # 工具脚本
├── requirements.txt        # Python依赖
├── STRUCTURE.md           # 项目结构文档
├── src/                   # 源代码目录
│   ├── reddit_scraper.py     # Reddit API集成
│   ├── newsletter_sender.py  # 邮件发送模块
│   ├── database_manager.py   # 数据库管理
│   └── config_manager.py     # 配置管理
├── templates/             # 邮件模板
│   ├── newsletter_template.html
│   └── newsletter_template.txt
├── tools/                 # 开发工具
│   ├── manage.py             # 管理脚本
│   ├── preview_server.py     # 模板预览服务器
│   └── oauth_helper.py       # Reddit OAuth设置
├── tests/                 # 测试模块
│   ├── README.md             # 测试文档
│   ├── run_tests.py          # 测试运行器
│   ├── test_reddit_connection.py   # Reddit API测试
│   ├── test_email_connection.py    # 邮件功能测试
│   ├── test_database.py            # 数据库测试
│   └── test_full_system.py         # 完整系统测试
├── data/                  # 应用数据
│   ├── database/             # 数据库文件
│   ├── logs/                 # 日志文件
│   └── backups/              # 备份文件
├── backup/                # 备份存档
└── .github/
    └── copilot-instructions.md
```

## 数据库

项目使用 SQLite 数据库存储：

- **posts 表** - 已发送的帖子记录
- **newsletter_logs 表** - Newsletter 发送日志
- **settings 表** - 配置信息（预留）

数据库文件默认为`data/database/reddit_newsletter.db`，可通过`DATABASE_PATH`配置。

## 🛠️ 管理工具

项目提供了完整的管理工具集，位于 `tools/manage.py`：

### 配置验证

```bash
python tools/manage.py validate-config
```

验证 `.env` 配置文件是否正确，显示配置摘要。

### 连接测试

```bash
# 测试 Reddit API 连接
python tools/manage.py test-reddit

# 测试邮件发送
python tools/manage.py test-email

# 运行完整测试
python tools/manage.py test-all
```

### 手动操作

```bash
# 立即发送 Newsletter（不等待定时）
python tools/manage.py send-now

# 查看统计信息
python tools/manage.py stats

# 清理旧数据（默认90天前）
python tools/manage.py cleanup --days 90
```

### 开发工具

#### 模板预览服务器

启动实时模板预览服务器：

```bash
python tools/preview_server.py
```

访问 http://localhost:5000/preview 查看邮件模板效果。

#### OAuth 设置助手

设置 Reddit OAuth 认证：

```bash
python tools/oauth_helper.py
```

## 部署建议

### Windows 服务

1. 使用`nssm`将 Python 脚本安装为 Windows 服务
2. 或使用任务计划程序定时运行

### Linux 服务

1. 创建 systemd 服务文件
2. 使用 cron 定时任务

### Docker 部署

项目支持 Docker 部署（需要额外配置 Dockerfile）。

## 故障排除

### 常见问题

1. **Reddit API 连接失败**

   - 检查 client_id 和 client_secret 是否正确
   - 确认 Reddit 账户凭据正确
   - 检查网络连接

2. **邮件发送失败**

   - 确认 SMTP 服务器设置正确
   - 检查邮箱是否启用了应用密码
   - 验证收件人邮箱地址

3. **数据库错误**
   - 检查数据库文件权限
   - 确认 SQLite 可正常访问

### 日志查看

程序运行日志保存在`reddit_newsletter.log`文件中，包含详细的运行信息和错误信息。

## 贡献

欢迎提交问题和功能请求！

## 许可证

MIT License

## 注意事项

- 请遵守 Reddit API 使用条款
- 避免频繁请求，注意 API 限制
- 保护好 API 密钥和邮箱密码
- 合理设置抓取频率和数量
