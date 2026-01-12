# Reddit Newsletter Bot 🚀

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Reddit API](https://img.shields.io/badge/Reddit-API-orange.svg)](https://www.reddit.com/dev/api/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://www.postgresql.org/)

一个智能的 Reddit 热门帖子聚合器，自动生成精美的 Newsletter 并定时发送。集成 OpenAI GPT 进行内容总结和分析，使用 PostgreSQL 数据库。

## ✨ 主要功能

- 🔥 **多版块热门抓取** - 支持自定义 Subreddit 和抓取规则
- 🤖 **AI 智能总结** - GPT 驱动的帖子总结和受欢迎度分析
- 📧 **精美邮件模板** - 响应式 HTML 设计，支持纯文本版本
- ⏰ **定时自动发送** - 可配置的发送时间和频率
- 💾 **PostgreSQL 数据库** - 可靠的数据存储，支持云端部署
- 📊 **统计与管理** - 发送成功率、内容统计等
- 🛠️ **丰富的工具** - 测试、管理、清理等实用工具

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- PostgreSQL 数据库

### 2. 安装

```bash
git clone https://github.com/jayneechiu/newsea.git
cd newsea
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
# 或安装统一后端依赖
pip install -r backend/api/requirements.txt
```

### 3. 配置数据库

**选项 1：使用 Azure PostgreSQL (推荐)**

1. 在 [Azure Portal](https://portal.azure.com/) 创建 PostgreSQL 服务
2. 配置防火墙规则允许你的 IP
3. 复制数据库连接 URL

**选项 2：使用本地 PostgreSQL**

```bash
# Windows (需要管理员权限)
.\install_postgresql.bat

# 或手动安装
choco install postgresql -y
```

### 4. 配置环境变量

复制配置模板：

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

编辑 `.env` 文件，填入配置信息：

```env
# Reddit API 配置
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# PostgreSQL 数据库配置
DATABASE_URL=postgresql://username:password@host:port/database

# 邮件配置
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient@example.com
```

### 5. 测试和运行

```bash
# 测试数据库连接
python tests/test_postgres_connection.py

# 测试 Reddit 连接
python tests/test_reddit_connection.py

# 测试邮件发送
python tests/test_email_connection.py

# 运行 Scraper（连接自检，安全不发送）
python backend/scraper/run_job.py --test

# 运行 Scraper（实际发送/定时逻辑）
python backend/scraper/run_job.py
```

## ⚙️ 配置说明

### Reddit API 配置

1. 访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. 创建新应用（选择 "script" 类型）
3. 在 `.env` 中配置相关参数

### PostgreSQL 数据库配置

**Azure PostgreSQL (推荐):**

```env
DATABASE_URL=postgresql://username:password@your-server.postgres.database.azure.com:5432/postgres
```

**本地数据库:**

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/reddit_newsletter
```

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

## 🛠️ 开发和测试

```bash
# 运行测试
python tests/test_postgres_connection.py  # PostgreSQL 测试
python tests/test_reddit_connection.py    # Reddit API 测试
python tests/test_email_connection.py     # 邮件发送测试
python tests/test_full_system.py          # 完整系统测试

# 运行 API 服务
uvicorn backend.api.main:app --reload --port 8000

# 运行 Scraper
python backend/scraper/run_job.py          # 定时/实际运行
python backend/scraper/run_job.py --test   # 连接自检（不发送）
```

## 📁 项目结构

```
├── backend/               # 后端（API + Scraper）
│   ├── api/
│   │   ├── main.py          # FastAPI 应用入口
│   │   ├── Dockerfile       # 统一后端镜像
│   │   └── requirements.txt # 后端依赖（API+Scraper）
│   └── scraper/
│       ├── run_job.py
│       ├── config_manager.py
│       ├── reddit_scraper.py
│       ├── chatgpt_client.py
│       ├── newsletter_sender.py
│       └── database_manager.py
├── templates/             # 邮件模板
│   ├── newsletter_template.txt   # 纯文本模板
│   └── newsletter_template2.html # HTML 模板
├── tests/                 # 测试模块
│   ├── test_postgres_connection.py # PostgreSQL 连接测试
│   ├── test_reddit_connection.py   # Reddit API 测试
│   ├── test_email_connection.py    # 邮件功能测试
│   └── test_full_system.py         # 完整系统测试
├── .github/               # CI/CD 配置
└── .env.example           # 环境变量配置模板
```

## 📊 功能亮点

### AI 智能总结

- 使用 GPT 对每个热门帖子进行总结和分析
- 生成个性化的编辑寄语
- 智能识别帖子受欢迎的原因

### PostgreSQL 数据库

- 使用 PostgreSQL 进行可靠的数据存储
- 支持云端数据库（Azure PostgreSQL、Supabase 等）
- 完整的数据持久化和历史记录
- 自动表结构初始化

### 灵活配置

- 支持多个 Subreddit 同时抓取
- 可配置的帖子数量和过滤条件
- 灵活的发送时间和频率设置

## 🔧 开发

### 环境要求

- Python 3.11+
- PostgreSQL 数据库
- 网络连接（用于 API 调用）

### 测试

```bash
# 测试数据库连接
python tests/test_postgres_connection.py

# 测试 Reddit API
python tests/test_reddit_connection.py

# 测试邮件发送
python tests/test_email_connection.py

# 完整系统测试
python tests/test_full_system.py
```

### 数据库

项目使用 PostgreSQL 数据库存储（Schema V2）：

- **subreddits** — 管理 Subreddit 元信息与每日热帖缓存（`daily_hot_post_ids`）
- **reddit_posts** — 存储帖子内容与 GPT 摘要（含 `score`、`fetch_date`、`gpt_summary`）
- **newsletter_logs** — Newsletter 发送日志（全局）
- 可选：**users** 与 **user_newsletter_logs** — 用户与个性化发送日志（后续扩展）

数据库连接通过 `DATABASE_URL` 环境变量配置。系统启动时自动初始化所需表（见 [docs/database_schema_v2.md](docs/database_schema_v2.md)）。

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
- [psycopg2](https://www.psycopg.org/) - PostgreSQL 适配器

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**

   - 检查 `DATABASE_URL` 配置是否正确
   - 确认数据库服务运行正常
   - 验证网络连接

2. **Reddit API 连接失败**

   - 检查 Reddit API 凭据
   - 确认网络连接
   - 检查 API 限制

3. **邮件发送失败**
   - 确认 SMTP 配置正确
   - 检查邮箱应用密码
   - 验证收件人地址

### 日志查看

运行日志默认输出到控制台（stdout），可在本地终端或部署平台的日志面板查看。若需要持久化到文件，可后续启用文件日志并自定义保存路径。
