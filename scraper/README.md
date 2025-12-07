# Scraper Service

定时 Reddit 爬虫和 Newsletter 生成器。

## 功能特性

- 📅 定时爬取 Reddit 内容
- 🤖 使用 ChatGPT 自动生成 newsletter
- 📧 自动发送邮件
- 💾 数据库存储帖子
- 📊 任务统计和日志
- ⚡ 立即执行模式（测试用）

## 运行模式

### Schedule 模式（默认）

按计划定时运行（例如：周一/周三/周五 上午 9 点）

```bash
python main.py
```

### Immediate 模式

立即执行一次（用于测试）

```bash
RUN_MODE=immediate python main.py
```

## 配置

通过环境变量配置：

- `SCHEDULE_TIME` - 运行时间（默认："09:00"）
- `SCHEDULE_DAYS` - 运行日期（默认："monday,wednesday,friday"）
- `RUN_MODE` - "schedule" 或 "immediate"（默认："schedule"）

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（使用根目录的 .env）
# 或复制：copy ..\.env.example .env

# 立即执行一次（Windows PowerShell）
$env:RUN_MODE="immediate"; python main.py
# 或 CMD: set RUN_MODE=immediate & python main.py

# 启动定时任务
python main.py
```

## Docker

```bash
# 构建镜像
docker build -t newsea-scraper:latest .

# Schedule 模式运行
docker run --env-file .env newsea-scraper:latest

# Immediate 模式（一次性）
docker run --env-file .env -e RUN_MODE=immediate newsea-scraper:latest
```

## Kubernetes CronJob

生产环境推荐使用 Kubernetes CronJob：

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: newsletter-scraper
spec:
  schedule: "0 9 * * 1,3,5" # 周一/周三/周五 上午9点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: scraper
              image: your-acr.azurecr.io/newsea-scraper:latest
              env:
                - name: RUN_MODE
                  value: "immediate"
```

## 日志

日志输出到：

- Console (stdout)
- 文件：`/app/logs/scraper.log`

## 环境变量

查看根目录的 `.env.example` 了解所需的环境变量配置。
