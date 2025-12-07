# API Service

基于 FastAPI 的 REST API 服务，为 Reddit Newsletter 系统提供接口。

## 功能特性

- 📡 RESTful API 接口
- 🔍 获取 Reddit 帖子
- 📧 Newsletter 生成和发送
- 👥 订阅管理
- 📊 统计分析
- 🔐 健康检查和监控

## API 接口

### Health Check

- `GET /` - Root endpoint
- `GET /health` - 详细健康检查

### Posts

- `GET /api/posts/{subreddit}` - 获取指定 subreddit 的帖子

### Newsletter

- `POST /api/newsletter/send` - 生成并发送 newsletter

### Statistics

- `GET /api/stats` - 获取系统统计信息

### Subscriptions

- `POST /api/subscribe` - 订阅 newsletter

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（使用根目录的 .env）
# 或复制：copy ..\.env.example .env

# 运行 API
uvicorn app:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看交互式 API 文档。

## Docker

```bash
# 构建镜像
docker build -t newsea-api:latest .

# 运行容器
docker run -p 8000:8000 --env-file .env newsea-api:latest
```

## 环境变量

查看根目录的 `.env.example` 了解所需的环境变量配置。
