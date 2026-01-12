# 数据库 Schema V2 - 精简版用户定制化 Newsletter 系统

## 📋 核心设计原则

- ✅ **简单实用**：只保留必需功能
- ✅ **性能优先**：缓存 subreddit 每日热帖，GPT 结果存在 post 表
- ✅ **规范化设计**：subreddit 作为独立实体，通过 ID 关联

---

## 🗄️ 表结构设计（4 个核心表）

### 1. `subreddits` - Subreddit 主表

**用途**：存储所有被订阅的 subreddit 元信息和每日热帖缓存

| 字段                 | 类型         | 说明                                    |
| -------------------- | ------------ | --------------------------------------- |
| `id`                 | SERIAL       | 主键（⭐ 核心外键）                     |
| `name`               | VARCHAR(100) | subreddit 名称（唯一，如'programming'） |
| `description`        | TEXT         | 描述（可选）                            |
| `daily_hot_post_ids` | JSONB        | ⭐ 当日热帖 ID 列表（缓存）             |
| `is_active`          | BOOLEAN      | 是否启用                                |
| `last_fetched_at`    | TIMESTAMP    | 最后抓取时间                            |
| `created_at`         | TIMESTAMP    | 创建时间                                |

**索引：**

- `idx_subreddits_name` - name (UNIQUE)
- `idx_subreddits_is_active` - is_active
- `idx_subreddits_last_fetched` - last_fetched_at

**daily_hot_post_ids 示例：**

```json
["abc123", "def456", "ghi789"]
```

**用途：**

- 缓存当日热帖 ID，避免重复查询
- 快速获取某 subreddit 的今日推荐内容
- 每日更新一次

---

### 2. `reddit_posts` - 帖子表（含 GPT 处理结果）

**用途**：存储所有抓取的帖子 + GPT 生成的摘要

| 字段                 | 类型        | 说明                      |
| -------------------- | ----------- | ------------------------- |
| `id`                 | VARCHAR(50) | Reddit post ID（主键）    |
| `subreddit_id`       | INTEGER     | ⭐ 外键 → subreddits.id   |
| `title`              | TEXT        | 标题                      |
| `url`                | TEXT        | 链接                      |
| `num_comments`       | INTEGER     | 评论数                    |
| `score`              | INTEGER     | 帖子分数（用于排序/筛选） |
| `created_utc`        | TIMESTAMP   | Reddit 创建时间           |
| `selftext`           | TEXT        | 正文内容                  |
| `over_18`            | BOOLEAN     | 是否 NSFW                 |
| **`gpt_summary`**    | TEXT        | ⭐ GPT 中文摘要           |
| **`gpt_summary_en`** | TEXT        | GPT 英文摘要（可选）      |
| `gpt_processed_at`   | TIMESTAMP   | GPT 处理完成时间          |
| `gpt_error`          | TEXT        | GPT 处理错误              |
| `fetch_date`         | DATE        | 抓取日期（用于清理）      |
| `created_at`         | TIMESTAMP   | 创建时间                  |

**索引：**

- `idx_reddit_posts_subreddit_id` - subreddit_id
- `idx_reddit_posts_fetch_date` - fetch_date
- `idx_reddit_posts_score` - score

**工作流程：**

```python
# 1. 抓取帖子时，先检查是否已存在
SELECT id FROM reddit_posts WHERE id = 'abc123'

# 2. 插入帖子（gpt_summary为NULL）
-- 注意：需提供 fetch_date（例如 CURRENT_DATE）以及可选的 score
INSERT INTO reddit_posts (id, subreddit_id, title, fetch_date, score, ...) VALUES (...)

# 3. 批量处理未生成摘要的帖子
SELECT * FROM reddit_posts
WHERE gpt_summary IS NULL
ORDER BY score DESC LIMIT 100

# 4. GPT处理后，更新摘要
UPDATE reddit_posts
SET gpt_summary = '...', gpt_processed_at = NOW()
WHERE id = 'abc123'
```

---

### 3. `users` - 用户表（含订阅信息）

**用途**：存储用户基本信息和订阅的 subreddit 列表

| 字段                        | 类型         | 说明                        |
| --------------------------- | ------------ | --------------------------- |
| `id`                        | SERIAL       | 主键                        |
| `email`                     | VARCHAR(255) | 邮箱（唯一）                |
| `username`                  | VARCHAR(100) | 用户名                      |
| `is_active`                 | BOOLEAN      | 是否激活（控制发送）        |
| `language`                  | VARCHAR(10)  | 语言偏好（默认 zh-CN）      |
| **`subscribed_subreddits`** | JSONB        | ⭐ 订阅的 subreddit ID 列表 |
| `frequency`                 | VARCHAR(20)  | 发送频率（daily/weekly）    |
| `created_at`                | TIMESTAMP    | 创建时间                    |
| `updated_at`                | TIMESTAMP    | 更新时间                    |

**索引：**

- `idx_users_email` - email
- `idx_users_is_active` - is_active

**subscribed_subreddits 示例：**

```json
[1, 3, 5, 8] // subreddit IDs
```

**查询示例：**

```sql
-- 获取用户订阅的所有subreddit详细信息
SELECT s.* FROM subreddits s
WHERE s.id = ANY(
  SELECT jsonb_array_elements_text(subscribed_subreddits)::int
  FROM users WHERE id = 1
)

-- 简化写法
SELECT * FROM users WHERE id = 1;
-- 然后在代码中解析 subscribed_subreddits
```

---

### 4. `user_newsletter_logs` - Newsletter 发送日志

**用途**：跟踪每个用户的 newsletter 发送历史（仅记录成功/失败）

| 字段               | 类型        | 说明                  |
| ------------------ | ----------- | --------------------- |
| `id`               | SERIAL      | 主键                  |
| `user_id`          | INTEGER     | 外键 → users.id       |
| `sent_at`          | TIMESTAMP   | 发送时间              |
| `status`           | VARCHAR(20) | 状态：success/failed  |
| `error_message`    | TEXT        | 错误信息（失败时）    |
| `posts_count`      | INTEGER     | 发送的帖子数          |
| `subreddits_count` | INTEGER     | 涉及的 subreddit 数量 |
| `created_at`       | TIMESTAMP   | 创建时间              |

**索引：**

- `idx_user_newsletter_logs_user_id` - user_id
- `idx_user_newsletter_logs_sent_at` - sent_at

---

## 🔄 完整工作流程

### 1️⃣ 抓取阶段

```python
# 1. 获取所有被订阅的subreddit（从users表去重）
all_user_subs = get_all_subscribed_subreddit_ids()  # 从JSONB中提取
active_subreddits = get_subreddits_by_ids(all_user_subs)

for subreddit in active_subreddits:
    # 2. 从Reddit API获取热帖
    hot_posts = fetch_from_reddit(subreddit.name)

    post_ids = []
    # 3. 插入到 reddit_posts 表（如果不存在）
    for post in hot_posts:
        insert_post_if_not_exists(
            post_id=post['id'],
            subreddit_id=subreddit.id,
            title=post['title'],
            ...
        )
        post_ids.append(post['id'])

    # 4. 更新 subreddit 的 daily_hot_post_ids
    update_subreddit_daily_posts(
        subreddit_id=subreddit.id,
        post_ids=post_ids
    )
```

### 2️⃣ GPT 处理阶段

```python
# 批量获取未处理的帖子（按分数降序）
unprocessed_posts = get_unprocessed_posts(limit=100)

for post in unprocessed_posts:
    try:
        # 调用GPT生成摘要
        summary = generate_gpt_summary(post.title, post.selftext)

        # 更新帖子
        update_post_gpt_summary(
            post_id=post.id,
            gpt_summary=summary,
            gpt_processed_at=datetime.now()
        )
    except Exception as e:
        update_post_gpt_error(post.id, str(e))
```

### 3️⃣ Newsletter 生成阶段

```python
# 获取今日要发送的用户（is_active=true, frequency=daily）
users = get_daily_newsletter_users()

for user in users:
    # 1. 直接从user.subscribed_subreddits获取订阅的subreddit IDs
    subreddit_ids = user.subscribed_subreddits  # [1, 3, 5, 8]

    # 2. 获取这些subreddit的详细信息
    subscribed_subreddits = get_subreddits_by_ids(subreddit_ids)

    # 3. 从每个subreddit的daily_hot_post_ids获取帖子
    all_posts = []
    for sub in subscribed_subreddits:
        posts = get_posts_by_ids(
            post_ids=sub.daily_hot_post_ids,
            has_gpt_summary=True
        )
        all_posts.extend(posts)

    # 4. 生成并发送newsletter
    send_newsletter(user, all_posts)

    # 5. 记录发送日志
    log_newsletter_sent(
        user_id=user.id,
        posts_count=len(all_posts),
        subreddits_count=len(subreddit_ids),
        status='success'
    )
```

---

## 📊 ER 图

```
┌─────────────┐
│ subreddits  │
│ (id, name,  │
│  hot_posts) │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴───────────┐
│  reddit_posts    │
│  (id, sub_id,    │
│   gpt_summary)   │
└──────────────────┘

┌──────────────────┐
│     users        │
│  (id, email,     │
│   subscribed_    │
│   subreddits)    │
└──────┬───────────┘
       │ 1
       │
       │ N
┌──────┴───────────┐
│user_newsletter   │
│     _logs        │
└──────────────────┘
```

---

## 🚀 数据库升级

```bash
# 升级数据库到 V2
python scripts/upgrade_database.py

# 回滚到 V1（警告：删除所有用户数据）
python scripts/upgrade_database.py rollback
```

---

## 🎯 使用示例

### 1. 创建用户并订阅 subreddit

```python
# 创建用户
user_id = create_user(
    email="user@example.com",
    username="tech_lover",
    language="zh-CN",
    subscribed_subreddits=[1, 3, 5],  # subreddit IDs
    frequency="daily"
)

# 更新订阅
update_user_subscriptions(
    user_id=user_id,
    subscribed_subreddits=[1, 3, 5, 8]  # 添加新的subreddit ID
)
```

### 2. 获取 subreddit 今日热帖

```python
# 通过缓存的post_ids快速获取
subreddit = get_subreddit_by_name("programming")
posts = get_posts_by_ids(
    post_ids=subreddit.daily_hot_post_ids,
    has_gpt_summary=True
)
```

### 3. 批量处理 GPT 摘要

```python
# 获取未处理的高分帖子
unprocessed = get_unprocessed_posts(
    min_score=100,
    limit=50
)

for post in unprocessed:
    summary = call_gpt_api(post)
    update_post_summary(post.id, summary)
```

---

## 🚀 下一步开发计划

1. **用户管理模块** (`src/user_manager.py`)

   - 用户 CRUD
   - 订阅管理

2. **Subreddit 管理** (`src/subreddit_manager.py`)

   - 抓取热帖
   - 更新 daily_hot_post_ids

3. **GPT 批处理** (`src/gpt_batch_processor.py`)

   - 批量生成摘要
   - 错误重试

4. **个性化 Newsletter** (`src/personalized_newsletter.py`)
   - 按用户订阅组装内容
   - 批量发送

---

## 📝 性能优化

### 1. GPT 处理优化

```sql
-- 只处理高分帖子
SELECT * FROM reddit_posts
WHERE gpt_summary IS NULL
  AND score >= 100
ORDER BY score DESC
LIMIT 100
```

### 2. 避免重复抓取

```sql
-- 检查是否需要重新抓取
SELECT * FROM subreddits
WHERE is_active = TRUE
  AND (last_fetched_at IS NULL
       OR last_fetched_at < NOW() - INTERVAL '1 hour')
```

### 3. 清理旧数据

```sql
-- 删除30天前的帖子
DELETE FROM reddit_posts
WHERE fetch_date < CURRENT_DATE - INTERVAL '30 days'
```
