# 分支管理策略

## 分支结构

### 主要分支

- **`main`** - 生产分支

  - 始终保持稳定可部署状态
  - 只接受来自 `dev` 分支的合并
  - 所有合并必须通过 Pull Request
  - 需要至少 1 个代码审查批准

- **`dev`** - 开发分支
  - 日常开发的主分支
  - 功能开发完成后合并到此分支
  - 定期合并到 `main` 分支发布

### 功能分支

- **`feature/*`** - 新功能开发

  - 从 `dev` 分支创建
  - 命名规范：`feature/功能名称`
  - 示例：`feature/email-template`, `feature/gpt-integration`
  - 完成后通过 PR 合并回 `dev`

- **`bugfix/*`** - Bug 修复

  - 从 `dev` 分支创建
  - 命名规范：`bugfix/问题描述`
  - 示例：`bugfix/email-sending-error`

- **`hotfix/*`** - 紧急修复
  - 从 `main` 分支创建
  - 修复生产环境的紧急问题
  - 完成后同时合并到 `main` 和 `dev`

## Pull Request 流程

1. **创建分支**

   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **开发和提交**

   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   git push origin feature/your-feature-name
   ```

3. **创建 Pull Request**

   - 在 GitHub 上创建 PR
   - 填写 PR 模板
   - 等待 CI 检查通过
   - 请求代码审查

4. **代码审查**

   - 至少需要 1 个审查者批准
   - 解决所有评论
   - CI 必须全部通过

5. **合并**
   - 使用 "Squash and merge" 保持提交历史清晰
   - 删除已合并的功能分支

## 提交信息规范

使用约定式提交（Conventional Commits）：

- `feat:` - 新功能
- `fix:` - Bug 修复
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建/工具链更新

示例：

```
feat: 添加newsletter template2模板
fix: 修复邮件发送失败问题
docs: 更新README配置说明
```

## 分支保护规则

### main 分支保护

- ✅ 需要 Pull Request 才能合并
- ✅ 需要至少 1 个审查批准
- ✅ 需要状态检查通过（CI）
- ✅ 需要分支为最新状态
- ✅ 禁止强制推送
- ✅ 禁止删除分支

### dev 分支保护

- ✅ 需要 Pull Request 才能合并
- ✅ 需要状态检查通过（CI）
- ✅ 禁止强制推送

## 发布流程

1. 确保 `dev` 分支所有功能已完成并测试
2. 创建 PR：`dev` → `main`
3. 更新版本号和 CHANGELOG
4. 等待 CI 通过和代码审查
5. 合并到 `main`
6. 在 `main` 分支打 tag：`v1.0.0`
7. 发布 Release notes

## 注意事项

- 始终从最新的 `dev` 分支创建功能分支
- 定期从 `dev` 拉取更新避免冲突
- 功能分支开发时间不应超过 3 天
- 保持提交粒度适中，每个提交应该是一个完整的逻辑单元
- 推送前先本地测试通过
