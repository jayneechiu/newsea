<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Reddit Newsletter Bot - Copilot 指令

这是一个 Reddit 热门帖子抓取和自动发送 Newsletter 的 Python 项目。

## 项目结构

- `main.py` - 主程序入口，包含定时调度逻辑
- `src/reddit_scraper.py` - Reddit API 集成，负责抓取热门帖子
- `src/newsletter_sender.py` - 邮件发送模块，支持 HTML 格式 Newsletter
- `src/database_manager.py` - SQLite 数据库管理，记录已发送帖子和统计信息
- `src/config_manager.py` - 配置管理，支持环境变量配置
- `tools.py` - 工具脚本，提供测试和管理功能
- `templates/newsletter_template.html` - Newsletter HTML 模板

## 开发规范

1. 使用类型提示（typing）
2. 遵循 PEP 8 代码规范
3. 添加适当的日志记录
4. 处理异常情况
5. 使用中文注释和日志消息

## 主要功能

- Reddit API 集成（使用 PRAW 库）
- 定时任务调度（使用 schedule 库）
- 邮件发送（SMTP 支持）
- 数据库管理（SQLite）
- 配置管理（dotenv）
- HTML 邮件模板（Jinja2）

## 配置文件

项目使用 `.env` 文件进行配置，包含 Reddit API 密钥、SMTP 设置、目标 Subreddit 等。
