# 数据库配置

此项目现在使用 **PostgreSQL** 作为数据库后端（之前使用 SQLite）。

## 数据库设置

Reddit Newsletter Bot 现在连接到 PostgreSQL 数据库（推荐：Railway）。

### 配置

在 `.env` 中配置 PostgreSQL 连接：

```env
# PostgreSQL 数据库（Azure / Supabase）
DATABASE_URL=postgresql://user:pass@host:port/database

# 或使用分离的变量
DB_HOST=your-host
DB_PORT=5432
DB_NAME=your-database
DB_USER=your-username
DB_PASSWORD=your-password
DB_SSLMODE=require
```

### 数据表

首次运行时将自动创建以下表：

- **posts** - 已发送的 Reddit 帖子记录和元数据
- **newsletter_logs** - Newsletter 发送统计和分析数据
- **settings** - 配置信息

### 测试

测试 PostgreSQL 连接：

```bash
python tests/test_postgres_connection.py
```
